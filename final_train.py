#!/usr/bin/env python3
import os, sys, json, time, gc
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import torch
torch.set_num_threads(8)

LOG_FILE = os.path.join(os.path.dirname(__file__) or ".", "final_train.log")
def log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)
    with open(LOG_FILE, "a") as f: f.write(f"[{ts}] {msg}\n")

log("="*60)
log("JEDI TRAINING — 36 examples, float16, aggressive GC")
log("="*60)

MODEL_ID = "LiquidAI/LFM2.5-1.2B-Instruct"
DATA_PATH = os.path.join(os.path.dirname(__file__) or ".", "train_29.jsonl")
ADAPTER_PATH = os.path.join(os.path.dirname(__file__) or ".", "jedi_final_adapter")

examples = []
with open(DATA_PATH) as f:
    for line in f:
        if line.strip():
            examples.append(json.loads(line))
log(f"Loaded {len(examples)} training examples")

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model

tok = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True, local_files_only=True)
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
log(f"Loaded in {time.time()-t0:.0f}s")

lora = LoraConfig(
    task_type="CAUSAL_LM", r=8, lora_alpha=16, lora_dropout=0.05,
    target_modules=["q_proj", "v_proj"], bias="none",
)
model = get_peft_model(model, lora)
model.train()
model.config.use_cache = False
n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
log(f"LoRA applied — {n_train/1e3:.0f}K trainable")

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
log(f"Tokenized {len(encoded)} examples, max_len={MAX_LEN}")

gc.collect()
log(f"RAM: {os.popen('free -h | grep Mem').read().strip()}")

optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=2e-4)
EPOCHS = 3
total = len(encoded)
log(f"Training: {total} examples x {EPOCHS} epochs")

gc.set_threshold(0)
start = time.time()
for epoch in range(EPOCHS):
    eloss = 0; steps = 0
    for idx in range(total):
        batch = [encoded[idx]]
        ids = torch.stack([b["input_ids"] for b in batch])
        mask = torch.stack([b["attention_mask"] for b in batch])
        lbls = torch.stack([b["labels"] for b in batch])
        t0 = time.time()
        out = model(input_ids=ids, attention_mask=mask, labels=lbls)
        lv = out.loss.item()
        out.loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step(); optimizer.zero_grad()
        del out, ids, mask, lbls, batch
        gc.collect()
        eloss += lv; steps += 1
        log(f"  E{epoch+1} step={steps}/{total} loss={lv:.4f} step_t={time.time()-t0:.1f}s")
    avg = eloss/steps
    log(f"  Epoch {epoch+1} avg_loss={avg:.4f}")
    ckpt = f"{ADAPTER_PATH}_e{epoch+1}"
    model.save_pretrained(ckpt)
    tok.save_pretrained(ckpt)
    log(f"  Checkpoint saved to {ckpt}")
    mem = os.popen('free -h | grep Mem').read().strip()
    log(f"  RAM after epoch: {mem}")

model.save_pretrained(ADAPTER_PATH)
tok.save_pretrained(ADAPTER_PATH)
tot = time.time()-start
log(f"\nAdapter saved to {ADAPTER_PATH}")
log(f"Total time: {tot:.0f}s ({tot/60:.1f}min)")
log("DONE")
