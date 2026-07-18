#!/usr/bin/env python3
import os, sys, json, time, gc, ctypes
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import torch
torch.set_num_threads(8)

ADAPTER_PATH = "/root/JEDI/jedi_lora_v4"
CORRECTIONS = "/root/JEDI/format_corrections.jsonl"
OUTPUT_ADAPTER = "/root/JEDI/jedi_lora_v5"
LOG_FILE = "/root/JEDI/train_v5.log"

def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f: f.write(line + "\n")

def free_mem():
    gc.collect()
    try: ctypes.CDLL('libc.so.6').malloc_trim(0)
    except: pass
    return os.popen('free -h 2>/dev/null | grep Mem').read().strip() or ""

log("="*60)
log("V5 FORMAT CORRECTIONS — continue from v4, 42 new examples, LR=3e-5")
log("="*60)

BASE_MODEL = "/root/.cache/huggingface/hub/models--LiquidAI--LFM2.5-1.2B-Instruct/snapshots/868df74dd56ff8a0c2ac5dbf281690c2dbebe4c9"

examples = []
with open(CORRECTIONS) as f:
    for line in f:
        if line.strip(): examples.append(json.loads(line))
log(f"Loaded {len(examples)} correction examples | RAM: {free_mem()}")

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, LoraConfig

tok = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True, local_files_only=True)
tok.pad_token = tok.eos_token

log("Loading base model + v4 adapter...")
t0 = time.time()
base = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    dtype=torch.float16,
    device_map="cpu",
    low_cpu_mem_usage=True,
    trust_remote_code=True,
    local_files_only=True,
)
model = PeftModel.from_pretrained(base, ADAPTER_PATH, is_trainable=True)
model.train()
model.config.use_cache = False
# Ensure LoRA params are trainable
for n, p in model.named_parameters():
    if 'lora_' in n:
        p.requires_grad_(True)
n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
log(f"v4 adapter loaded in {time.time()-t0:.0f}s | {n_train/1e3:.0f}K trainable params | RAM: {free_mem()}")

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
log(f"Tokenized {len(encoded)} ex, max_len={MAX_LEN}")

optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=3e-5)
EPOCHS = 2
total = len(encoded)
log(f"Training: {total} ex x {EPOCHS} epochs, LR=3e-5")

start = time.time()
for epoch in range(EPOCHS):
    eloss = 0; steps = 0
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
            optimizer.step(); optimizer.zero_grad()
            del out, ids, mask, lbls, batch; free_mem()
            eloss += lv; steps += 1
        except Exception as e:
            log(f"  E{epoch+1} FAIL idx={idx}: {e}")
            optimizer.zero_grad(); free_mem(); continue
        log(f"  E{epoch+1} {steps}/{total} loss={lv:.4f} t={time.time()-step_start:.1f}s")
    avg = eloss / steps
    log(f"  Epoch {epoch+1} avg_loss={avg:.4f}")
    ckpt = f"{OUTPUT_ADAPTER}_e{epoch+1}"
    model.save_pretrained(ckpt); tok.save_pretrained(ckpt)
    log(f"  Saved {ckpt}"); free_mem()

model.save_pretrained(OUTPUT_ADAPTER); tok.save_pretrained(OUTPUT_ADAPTER)
log(f"Done. Total: {time.time()-start:.0f}s | RAM: {free_mem()}")
