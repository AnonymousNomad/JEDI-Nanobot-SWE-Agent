#!/usr/bin/env python3
"""Continued training from existing LoRA adapter — add terminal examples."""
import os, sys, json, time, gc, ctypes
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import torch
torch.set_num_threads(8)

LOG_FILE = os.path.join(os.path.dirname(__file__) or ".", "continue_train.log")
ADAPTER_PATH = os.path.join(os.path.dirname(__file__) or ".", "jedi_nanobot_adapter")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__) or ".", "jedi_nanobot_adapter_v2")

def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f: f.write(line + "\n")

def free_mem():
    gc.collect()
    try: ctypes.CDLL('libc.so.6').malloc_trim(0)
    except: pass
    return os.popen('free -h | grep Mem').read().strip()

log("="*60)
log("CONTINUED TRAINING — 146 examples, from existing adapter, lower LR")
log("="*60)

BASE = "/root/.cache/huggingface/hub/models--LiquidAI--LFM2.5-1.2B-Instruct/snapshots/868df74dd56ff8a0c2ac5dbf281690c2dbebe4c9"
DATA_PATH = os.path.join(os.path.dirname(__file__) or ".", "merged_corpus_v2.jsonl")

examples = []
with open(DATA_PATH) as f:
    for line in f:
        if line.strip(): examples.append(json.loads(line))
log(f"Loaded {len(examples)} training examples")
log(f"RAM: {free_mem()}")

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

tok = AutoTokenizer.from_pretrained(BASE, local_files_only=True)
tok.pad_token = tok.eos_token

log("Loading base model...")
t0 = time.time()
model = AutoModelForCausalLM.from_pretrained(
    BASE, dtype=torch.float16, device_map="cpu",
    low_cpu_mem_usage=True, trust_remote_code=True, local_files_only=True,
)
log(f"Base loaded in {time.time()-t0:.0f}s")
log(f"RAM: {free_mem()}")

log("Loading existing LoRA adapter...")
model = PeftModel.from_pretrained(model, ADAPTER_PATH, is_trainable=True)
model.train()
model.config.use_cache = False
n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
log(f"LoRA loaded — {n_train/1e3:.0f}K trainable params")

MAX_LEN = 256
encoded = []
for i, ex in enumerate(examples):
    text = ""
    for msg in ex["messages"]:
        role = msg["role"]
        content = msg["content"]
        if role == "system":
            text += f"<|im_start|>system\n{content}<|im_end|>\n"
        elif role == "user":
            text += f"<|im_start|>user\n{content}<|im_end|>\n"
        elif role == "assistant":
            text += f"<|im_start|>assistant\n{content}<|im_end|>\n"
    text += "<|im_start|>assistant\n"
    t = tok(text, truncation=True, max_length=MAX_LEN, padding=False, return_tensors="pt")
    encoded.append((t["input_ids"], t["attention_mask"]))
    if (i+1) % 20 == 0 or i == len(examples)-1:
        log(f"  encoded {i+1}/{len(examples)}")

# Pad sequences to same length
max_len = max(e[0].shape[1] for e in encoded)
input_ids_list, attn_mask_list, labels_list = [], [], []
for e in encoded:
    ids = e[0]
    mask = e[1]
    pad_len = max_len - ids.shape[1]
    ids = torch.nn.functional.pad(ids, (0, pad_len), value=tok.pad_token_id)
    mask = torch.nn.functional.pad(mask, (0, pad_len), value=0)
    lbl = ids.clone()
    lbl[mask == 0] = -100  # ignore padding in loss
    input_ids_list.append(ids)
    attn_mask_list.append(mask)
    labels_list.append(lbl)
input_ids = torch.cat(input_ids_list)
attn_mask = torch.cat(attn_mask_list)
labels = torch.cat(labels_list)

dataset = torch.utils.data.TensorDataset(input_ids, attn_mask, labels)
loader = torch.utils.data.DataLoader(dataset, batch_size=1, shuffle=True)

from transformers import get_scheduler

# Lower LR to 2e-5 for continued training
optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
scheduler = get_scheduler("cosine", optimizer=optimizer, num_warmup_steps=5, num_training_steps=len(loader))

log(f"Starting training — {len(loader)} steps, LR=2e-5")
t0_total = time.time()
for epoch in range(1):
    log(f"Epoch {epoch+1}/1")
    for step, batch in enumerate(loader):
        step_t0 = time.time()
        b_ids, b_mask, b_labels = batch
        out = model(input_ids=b_ids, attention_mask=b_mask, labels=b_labels)
        loss = out.loss
        loss.backward()
        optimizer.step()
        scheduler.step()
        optimizer.zero_grad()
        free_mem()
        step_time = time.time() - step_t0
        if step % 10 == 0 or step == len(loader)-1:
            log(f"  step {step+1}/{len(loader)} loss={loss.item():.4f} lr={scheduler.get_last_lr()[0]:.2e} ({step_time:.0f}s) ram={free_mem()}")

log(f"Training done in {time.time()-t0_total:.0f}s")
log(f"Saving adapter to {OUTPUT_PATH}")
model.save_pretrained(OUTPUT_PATH)
tok.save_pretrained(OUTPUT_PATH)
log("Done!")
