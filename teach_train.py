#!/usr/bin/env python3
"""Fast float16 training on correction data — same approach as qlora_lfm_v2.py"""
import os, sys, json, time, gc
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import torch
torch.set_num_threads(8)

LOG_FILE = "teach_train.log"
def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f: f.write(line + "\n")

log("=" * 60)
log("Teaching: float16 training on correction data")
log("=" * 60)

MODEL_ID = "LiquidAI/LFM2.5-1.2B-Instruct"
ADAPTER_PATH = "/root/JEDI/jedi_fast_adapter"

# Load correction data
corr_path = "/root/JEDI/correction_data_r1.jsonl"
examples = []
with open(corr_path) as f:
    for line in f:
        if line.strip():
            examples.append(json.loads(line))
log(f"Loaded {len(examples)} correction examples")

# Load in float16 (like original working script)
from transformers import AutoTokenizer, AutoModelForCausalLM
tok = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True, local_files_only=True)
tok.pad_token = tok.eos_token
log(f"Tokenizer ready — vocab={tok.vocab_size}")

log("Loading LFM2.5 in float16...")
t0 = time.time()
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID, dtype=torch.float16, device_map="cpu",
    low_cpu_mem_usage=True, trust_remote_code=True, local_files_only=True,
)
log(f"Model loaded — {sum(p.numel() for p in model.parameters())/1e6:.1f}M params in {time.time()-t0:.0f}s")

gc.collect()
log(f"RAM: {os.popen('free -h | grep Mem').read().strip()}")

# LoRA (small)
from peft import LoraConfig, get_peft_model, TaskType
lora = LoraConfig(task_type=TaskType.CAUSAL_LM, r=8, lora_alpha=16, lora_dropout=0.05, target_modules=["q_proj","v_proj"], bias="none")
model = get_peft_model(model, lora)
model.train()
model.config.use_cache = False
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
log(f"LoRA applied — {trainable/1e3:.0f}K trainable")

gc.collect()
log(f"RAM after LoRA: {os.popen('free -h | grep Mem').read().strip()}")

# Tokenize
MAX_LEN = 256
encoded = []
for ex in examples:
    text = ""
    for m in ex["messages"]:
        text += f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n"
    text += "<|im_start|>assistant\n"
    t = tok(text, truncation=True, max_length=MAX_LEN, padding="max_length", return_tensors="pt")
    labels = t["input_ids"].clone()
    labels[t["attention_mask"] == 0] = -100
    encoded.append({"input_ids": t["input_ids"].squeeze(), "attention_mask": t["attention_mask"].squeeze(), "labels": labels.squeeze()})
log(f"Tokenized {len(encoded)} examples")

optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=2e-4)
BATCH_SIZE = 2
EPOCHS = 2
total = len(encoded)
steps_total = ((total - 1) // BATCH_SIZE) + 1
log(f"Training: {total} examples x {EPOCHS} epochs, batch={BATCH_SIZE}")

start = time.time()
for epoch in range(EPOCHS):
    eloss = 0
    steps = 0
    i = 0
    while i < total:
        be = min(i + BATCH_SIZE, total)
        batch = encoded[i:be]
        ids = torch.stack([b["input_ids"] for b in batch])
        mask = torch.stack([b["attention_mask"] for b in batch])
        lbls = torch.stack([b["labels"] for b in batch])
        
        t0 = time.time()
        out = model(input_ids=ids, attention_mask=mask, labels=lbls)
        lv = out.loss.item()
        out.loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        optimizer.zero_grad()
        del out, ids, mask, lbls, batch
        
        eloss += lv
        steps += 1
        i = be
        log(f"  E{epoch+1} step={steps}/{steps_total} loss={lv:.4f} step_t={time.time()-t0:.1f}s")
        
        # Force cleanup every 5 steps
        if steps % 5 == 0:
            gc.collect()
    
    log(f"  Epoch {epoch+1} avg_loss={eloss/steps:.4f}")

# Save
model.save_pretrained(ADAPTER_PATH)
tok.save_pretrained(ADAPTER_PATH)
log(f"Adapter saved to {ADAPTER_PATH}")
total_t = time.time() - start
log(f"Total: {total_t:.0f}s ({total_t/60:.1f}min)")
log("DONE")
