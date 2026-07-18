"""
Nanobot conditioner system.
Each nanobot = a set of tiny bias vectors grafted onto MLP output layers.
Composition at inference: model spawn string -> look up conditioner combo -> apply biases.
Conditioners stay in RAM permanently. No spawning/despawning overhead.
"""
import os, json, time, gc, ctypes
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.set_num_threads(8)

MODEL_PATH = "/root/.cache/huggingface/hub/models--LiquidAI--LFM2.5-1.2B-Instruct/snapshots/868df74dd56ff8a0c2ac5dbf281690c2dbebe4c9"

class ConditionerBank(nn.Module):
    """
    A bank of tiny learnable bias vectors grafted onto MLP outputs.
    
    Architecture:
    - N primitives, each M layers × hidden_dim params
    - Each primitive is a learned offset applied AFTER the MLP's down_proj
    - At inference: model spawns nanobot -> router loads composition -> forward applies biases
    
    For LFM 2.5:
    - 16 layers total
    - We hook 6 layers (early: 1,3  mid: 6,9  late: 12,15)
    - Each conditioner: 6 layers × 2048 hidden = 12,288 params
    - 30 primitives = 368,640 params = ~0.03% of model size
    """
    
    def __init__(self, hidden_dim=2048, n_layers=6, n_primitives=30):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.n_layers = n_layers
        self.n_primitives = n_primitives
        
        self.biases = nn.Parameter(torch.zeros(n_primitives, n_layers, hidden_dim))
        nn.init.normal_(self.biases, mean=0.0, std=0.01)
        
        # Composition matrix: each nanobot type = combination of primitives
        # Learnable during training
        self.router = nn.Linear(hidden_dim, n_primitives, bias=False)
        nn.init.normal_(self.router.weight, mean=0.0, std=0.005)
        
    def get_composition(self, hidden_state):
        """Route hidden state to primitive composition weights."""
        # hidden_state: [batch, seq_len, hidden_dim]
        pool = hidden_state.mean(dim=1)  # [batch, hidden_dim]
        logits = self.router(pool)       # [batch, n_primitives]
        weights = F.softmax(logits, dim=-1)  # [batch, n_primitives]
        # Weighted sum of primitive biases
        # biases: [n_primitives, n_layers, hidden_dim]
        composed = torch.einsum('bp,plh->blh', weights, self.biases)  # [batch, n_layers, hidden_dim]
        return composed


class ConditionerHook:
    """
    Forward hook that applies conditioner biases to MLP outputs.
    """
    
    def __init__(self, layer_indices, conditioner_bank):
        self.layer_indices = layer_indices  # which of our 6 slots map to which model layers
        self.active_biases = None  # [batch, 6, hidden] or None
        self.handles = []
        
    def set_biases(self, bias_tensor):
        """Set active biases. bias_tensor: [batch, n_layers, hidden]"""
        self.active_biases = bias_tensor.detach()
        
    def clear(self):
        self.active_biases = None

    def make_hook(self, layer_idx_in_cond):
        """Create a hook for a specific model layer."""
        def hook_fn(module, input, output):
            if self.active_biases is not None:
                bias = self.active_biases[:, layer_idx_in_cond, :]  # [batch, hidden]
                # Apply bias to MLP output (typically the hidden state before residual)
                if isinstance(output, tuple):
                    modified = output[0] + bias.unsqueeze(1)
                    return (modified,) + output[1:]
                else:
                    return output + bias.unsqueeze(1)
            return output
        return hook_fn


class NanobotRouter:
    """
    Text-level router that detects spawn tokens and activates conditioner compositions.
    """
    
    def __init__(self, conditioner_bank, hook):
        self.bank = conditioner_bank
        self.hook = hook
        self.nanobot_registry = {
            "scan": [0, 1, 2],      # primitives 0,1,2
            "trace": [3, 4, 5],
            "fix": [6, 7, 8],
            "build": [9, 10, 11],
            "verify": [12, 13, 14],
            "audit": [15, 16, 17],
            "inspect": [0, 3, 15],
            "diagnose": [1, 4, 16],
            "construct": [6, 9, 17],
            "patch": [7, 10, 13],
            "test": [12, 14, 8],
            "analyze": [0, 3, 4],
            "coordinate": [18, 19, 20],
            "decompose": [21, 22, 23],
            "synthesize": [24, 25, 26],
        }
        
    def detect_and_activate(self, generated_text):
        """Parse generated text for [Spawn: type] and set appropriate biases."""
        import re
        match = re.search(r'\[Spawn:\s*(\w+)', generated_text)
        if not match:
            return None
        
        nanobot_type = match.group(1).lower()
        if nanobot_type not in self.nanobot_registry:
            # Try fuzzy match
            for key in self.nanobot_registry:
                if key in nanobot_type or nanobot_type in key:
                    nanobot_type = key
                    break
            else:
                return None
        
        primitives = self.nanobot_registry[nanobot_type]
        # Sum the primitive biases for this composition
        bias = self.bank.biases[primitives].sum(dim=0)  # [n_layers, hidden]
        self.hook.set_biases(bias.unsqueeze(0))  # add batch dim
        return nanobot_type
        
    def clear(self):
        self.hook.clear()


def build_conditioner_system(model):
    """
    Graft conditioners onto a loaded model.
    Returns (conditioner_bank, hook, router).
    
    Model: a PeftModel or base model with 16 layers of LFM architecture.
    """
    hidden_dim = model.config.hidden_size  # 2048
    n_layers = model.config.num_hidden_layers  # 16
    
    # Select 6 target layers evenly distributed
    step = max(1, n_layers // 6)
    target_layers = [i * step for i in range(6)]  # [0, 2, 5, 8, 10, 13] for 16
    
    conditioner_bank = ConditionerBank(hidden_dim=hidden_dim, n_layers=6, n_primitives=30)
    
    # Find MLP output modules
    mlp_modules = []
    actual_indices = []
    for i in range(n_layers):
        if i in target_layers:
            idx_in_cond = target_layers.index(i)
            # Try common MLP module names
            found = False
            for name, mod in model.named_modules():
                if f"layers.{i}." in name and ("mlp" in name or "feed_forward" in name or "fc" in name):
                    if "down_proj" in name or "fc2" in name or "output" in name:
                        mlp_modules.append(mod)
                        actual_indices.append(idx_in_cond)
                        found = True
                        break
            if not found:
                # Fallback: look for any layer module
                for name, mod in model.named_modules():
                    if f"layers.{i}." in name and "post_attention" in name or "ffn" in name:
                        mlp_modules.append(mod)
                        actual_indices.append(idx_in_cond)
                        break
    
    hook = ConditionerHook(actual_indices, conditioner_bank)
    for idx, mod in enumerate(mlp_modules):
        layer_idx = actual_indices[idx]
        handle = mod.register_forward_hook(hook.make_hook(layer_idx))
        hook.handles.append(handle)
    
    router = NanobotRouter(conditioner_bank, hook)
    
    return conditioner_bank, hook, router


def save_conditioners(bank, path="/root/JEDI/conditioner_bank.pt"):
    """Save trained conditioner weights."""
    torch.save({
        'biases': bank.biases.data,
        'router_weight': bank.router.weight.data,
    }, path)
    print(f"Conditioners saved to {path}")


def load_conditioners(bank, path="/root/JEDI/conditioner_bank.pt"):
    """Load trained conditioner weights."""
    data = torch.load(path, map_location='cpu')
    bank.biases.data = data['biases']
    bank.router.weight.data = data['router_weight']
    print(f"Conditioners loaded from {path}")


def train_conditioners(model, tokenizer, conditioner_bank, hook, router,
                       examples, epochs=5, lr=1e-4, max_len=256):
    """
    Train conditioner primitives on nanobot examples.
    The base model + LoRA are frozen. Only conditioners train.
    """
    for p in model.parameters():
        p.requires_grad = False
    
    conditioner_bank.train()
    conditioner_bank.router.train()
    
    optimizer = torch.optim.AdamW([
        {'params': conditioner_bank.biases, 'lr': lr},
        {'params': conditioner_bank.router.parameters(), 'lr': lr * 2},
    ])
    
    # Pre-tokenize
    encoded = []
    for ex in examples:
        text = "".join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in ex['messages'])
        text += "<|im_start|>assistant\n"
        t = tokenizer(text, truncation=True, max_length=max_len, padding="max_length", return_tensors="pt")
        labels = t['input_ids'].clone()
        labels[t['attention_mask'] == 0] = -100
        encoded.append({
            'input_ids': t['input_ids'].squeeze(),
            'attention_mask': t['attention_mask'].squeeze(),
            'labels': labels.squeeze(),
        })
    
    total = len(encoded)
    print(f"Training {conditioner_bank.n_primitives} conditioners on {total} examples x {epochs} epochs")
    
    for epoch in range(epochs):
        eloss = 0
        for idx in range(total):
            batch = [encoded[idx]]
            ids = torch.stack([b['input_ids'] for b in batch])
            mask = torch.stack([b['attention_mask'] for b in batch])
            lbls = torch.stack([b['labels'] for b in batch])
            
            # Get hidden state from the model's embedding + first few layers
            # to route conditioners
            with torch.no_grad():
                embeds = model.get_input_embeddings()(ids)
                pool = embeds.mean(dim=1)
            
            # Activate composition
            comp_biases = conditioner_bank.get_composition(pool)
            hook.set_biases(comp_biases)
            
            out = model(input_ids=ids, attention_mask=mask, labels=lbls)
            lv = out.loss.item()
            out.loss.backward()
            torch.nn.utils.clip_grad_norm_(conditioner_bank.parameters(), 1.0)
            optimizer.step()
            optimizer.zero_grad()
            
            hook.clear()
            del out, ids, mask, lbls, batch, embeds, pool, comp_biases
            gc.collect()
            
            eloss += lv
            if (idx + 1) % 20 == 0:
                print(f"  E{epoch+1} step={idx+1}/{total} loss={lv:.4f}")
        
        avg = eloss / total
        print(f"  Epoch {epoch+1} avg_loss={avg:.4f}")
        save_conditioners(conditioner_bank)
    
    print("Conditioner training complete")
