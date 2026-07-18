#!/usr/bin/env python3
import os, sys, json, time, gc, ctypes, traceback
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import torch

torch.set_num_threads(8)

LOG_FILE = os.path.join(os.path.dirname(__file__) or ".", "nanobot_train.log")
ADAPTER_PATH = os.path.join(os.path.dirname(__file__) or ".", "jedi_nanobot_adapter")

def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f: f.write(line + "\n")

def free_mem():
    """Release Python memory back to OS."""
    gc.collect()
    if hasattr(gc, 'set_threshold'):
        gc.set_threshold(0)
    try:
        ctypes.CDLL('libc.so.6').malloc_trim(0)
    except:
        pass
    try:
        mem = os.popen('free -h | grep Mem').read().strip()
        return mem
    except:
        return ""

log("="*60)
log("NANOBOT TRAINING — 115 examples, float16, MAX_LEN=256, OS mem release")
log("="*60)

MODEL_ID = "/root/.cache/huggingface/hub/models--LiquidAI--LFM2.5-1.2B-Instruct/snapshots/868df74dd56ff8a0c2ac5dbf281690c2dbebe4c9"
DATA_PATH = os.path.join(os.path.dirname(__file__) or ".", "merged_corpus.jsonl")

examples = []
with open(DATA_PATH) as f:
    for line in f:
        if line.strip():
            examples.append(json.loads(line))
log(f"Loaded {len(examples)} training examples")
log(f"RAM before model load: {free_mem()}")

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model

tok = AutoTokenizer.from_pretrained(MODEL_ID, local_files_only=True)
tok.pad_token = tok.eos_token

log("Loading float16 model...")
t0 = time.time()
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype=torch.float16,
    device_map="cpu",
    low_cpu_mem_usage=True,
    trust_remote_code=True,
    local_files_only=True,
)
log(f"Model loaded in {time.time()-t0:.0f}s")
log(f"RAM after model load: {free_mem()}")

lora = LoraConfig(
    task_type="CAUSAL_LM", r=8, lora_alpha=16, lora_dropout=0.05,
    target_modules=["q_proj", "v_proj"], bias="none",
)
model = get_peft_model(model, lora)
model.train()
model.config.use_cache = False
n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
log(f"LoRA applied — {n_train/1e3:.0f}K trainable params")
log(f"RAM after LoRA: {free_mem()}")

MAX_LEN = 256
encoded = []
for i, ex in enumerate(examples):
    text = ""
    for m in ex["messages"]:
        text += f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n"
    text += "<|im_start|>assistant\n"
    t = tok(text, truncation=True, max_length=MAX_LEN, padding="max_length", return_tensors="pt")
    labels = t["input_ids"].clone()
    labels[t["attention_mask"] == 0] = -100
    encoded.append({
        "input_ids": t["input_ids"].squeeze(),
        "attention_mask": t["attention_mask"].squeeze(),
        "labels": labels.squeeze()
    })
    if (i+1) % 50 == 0:
        log(f"  Tokenized {i+1}/{len(examples)}")
        free_mem()

log(f"Tokenized {len(encoded)} examples, max_len={MAX_LEN}")
free_mem()
log(f"RAM after tokenization: {free_mem()}")

optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=2e-4)
EPOCHS = 3
total = len(encoded)
log(f"Training: {total} examples x {EPOCHS} epochs")
free_mem()

start = time.time()
for epoch in range(EPOCHS):
    eloss = 0
    steps = 0
    epoch_start = time.time()
    
    for idx in range(total):
        step_start = time.time()
        
        try:
            batch = [encoded[idx]]
            ids = torch.stack([b["input_ids"] for b in batch])
            mask = torch.stack([b["attention_mask"] for b in batch])
            lbls = torch.stack([b["labels"] for b in batch])
            
            out = model(input_ids=ids, attention_mask=mask, labels=lbls)
            lv = out.loss.item()
            out.loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            optimizer.zero_grad()
            
            del out, ids, mask, lbls, batch
            free_mem()
            
            eloss += lv
            steps += 1
        except Exception as e:
            log(f"  E{epoch+1} FAILED at idx={idx}: {e}")
            log(traceback.format_exc())
            optimizer.zero_grad()
            free_mem()
            continue
        
        step_t = time.time() - step_start
        log(f"  E{epoch+1} step={steps}/{total} loss={lv:.4f} step_t={step_t:.1f}s mem={free_mem()}")
    
    avg = eloss / steps
    mem = free_mem()
    epoch_t = time.time() - epoch_start
    log(f"  Epoch {epoch+1} avg_loss={avg:.4f} time={epoch_t:.0f}s mem={mem}")
    
    ckpt = f"{ADAPTER_PATH}_e{epoch+1}"
    model.save_pretrained(ckpt)
    tok.save_pretrained(ckpt)
    log(f"  Checkpoint saved to {ckpt}")
    
    # Force memory release between epochs
    free_mem()
    log(f"  RAM after epoch cleanup: {free_mem()}")

model.save_pretrained(ADAPTER_PATH)
tok.save_pretrained(ADAPTER_PATH)
tot = time.time() - start
log(f"\nAdapter saved to {ADAPTER_PATH}")
log(f"Total time: {tot:.0f}s ({tot/60:.1f}min)")
log(f"Final RAM: {free_mem()}")
log("DONE")
