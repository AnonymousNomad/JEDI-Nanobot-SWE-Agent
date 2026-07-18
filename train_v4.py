#!/usr/bin/env python3
import os, sys, json, time, gc, ctypes
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import torch
torch.set_num_threads(8)

LOG_FILE = os.path.join(os.path.dirname(__file__) or ".", "train_v4.log")
ADAPTER_PATH = os.path.join(os.path.dirname(__file__) or ".", "jedi_lora_v4")

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
log("JEDI ROUND 4 — base model, 149 ex, LR=5e-5, MAX_LEN=256, 3 epochs")
log("="*60)

MODEL_ID = "/root/.cache/huggingface/hub/models--LiquidAI--LFM2.5-1.2B-Instruct/snapshots/868df74dd56ff8a0c2ac5dbf281690c2dbebe4c9"
DATA_PATH = os.path.join(os.path.dirname(__file__) or ".", "comprehensive_v4.jsonl")

examples = []
with open(DATA_PATH) as f:
    for line in f:
        if line.strip(): examples.append(json.loads(line))
log(f"Loaded {len(examples)} examples | RAM: {free_mem()}")

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model

tok = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True, local_files_only=True)
tok.pad_token = tok.eos_token

log("Loading float16 base model...")
t0 = time.time()
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype=torch.float16,
    device_map="cpu",
    low_cpu_mem_usage=True,
    trust_remote_code=True,
    local_files_only=True,
)
log(f"Model loaded in {time.time()-t0:.0f}s | RAM: {free_mem()}")

lora = LoraConfig(
    task_type="CAUSAL_LM", r=8, lora_alpha=16, lora_dropout=0.05,
    target_modules=["q_proj", "v_proj"], bias="none",
)
model = get_peft_model(model, lora)
model.train()
model.config.use_cache = False
n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
log(f"LoRA {n_train/1e3:.0f}K params | RAM: {free_mem()}")

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
    encoded.append({"input_ids": t["input_ids"].squeeze(), "attention_mask": t["attention_mask"].squeeze(), "labels": labels.squeeze()})
    if (i+1) % 50 == 0: log(f"  Tokenized {i+1}/{len(examples)}")
log(f"Tokenized {len(encoded)} ex, max_len={MAX_LEN} | RAM: {free_mem()}")

optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=5e-5)
EPOCHS = 3
total = len(encoded)
log(f"Training: {total} ex x {EPOCHS} epochs, LR=5e-5")

start = time.time()
for epoch in range(EPOCHS):
    eloss = 0; steps = 0
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
            optimizer.step(); optimizer.zero_grad()
            del out, ids, mask, lbls, batch; free_mem()
            eloss += lv; steps += 1
        except Exception as e:
            log(f"  E{epoch+1} FAIL idx={idx}: {e}")
            optimizer.zero_grad(); free_mem(); continue
        log(f"  E{epoch+1} {steps}/{total} loss={lv:.4f} t={time.time()-step_start:.1f}s")
    avg = eloss / steps
    log(f"  Epoch {epoch+1} avg_loss={avg:.4f} time={time.time()-epoch_start:.0f}s")
    ckpt = f"{ADAPTER_PATH}_e{epoch+1}"
    model.save_pretrained(ckpt); tok.save_pretrained(ckpt)
    log(f"  Checkpoint saved to {ckpt}"); free_mem()

model.save_pretrained(ADAPTER_PATH); tok.save_pretrained(ADAPTER_PATH)
log(f"Done. Adapter saved. Total: {time.time()-start:.0f}s | RAM: {free_mem()}")
