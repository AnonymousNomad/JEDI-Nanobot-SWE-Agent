"""JEDI Fast Training — Float16 + batched LoRA on full 20K dataset"""
import os, sys, time, json, gc
os.environ["PYTORCH_NO_CUDA_MEMORY_CACHING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import torch

torch.set_num_threads(8)
torch.backends.mkldnn.enabled = True

RESUME = "--resume" in sys.argv
LOG_FILE = "train_fast.log"

def get_last_step():
    if not os.path.exists(LOG_FILE): return 0
    import re
    with open(LOG_FILE) as f:
        for line in f:
            m = re.search(r'step=(\d+)/', line)
            if m: return int(m.group(1))
    return 0

if not RESUME:
    with open(LOG_FILE, "w") as f: f.write("")

def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f: f.write(line + "\n")

log("=" * 60)
log("JEDI Fast Training — LFM2.5-1.2B-Instruct — Full 20K Dataset")
log("=" * 60)

MODEL_ID = "LiquidAI/LFM2.5-1.2B-Instruct"
DATA_PATH = "/root/JEDI/training_data_master.jsonl"
MAX_LEN = 128
BATCH_SIZE = 2
LORA_R = 8
LORA_ALPHA = 16
LR = 2e-4
EPOCHS = 1
SAVE_EVERY = 500

# Load + pre-tokenize
log("Loading tokenizer...")
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
tok.pad_token = tok.eos_token
log(f"Tokenizer ready — vocab={tok.vocab_size}")

log("Loading + tokenizing data...")
items = []
with open(DATA_PATH) as f:
    for line in f:
        if line.strip():
            items.append(json.loads(line))
log(f"Loaded {len(items)} examples")

cache_path = "pretokenized_cache.pt"
if os.path.exists(cache_path):
    log("Loading pre-tokenized cache...")
    encoded = torch.load(cache_path, weights_only=False)
    log(f"Loaded {len(encoded)} pre-tokenized examples")
else:
    log("Tokenizing (this may take a minute)...")
    encoded = []
    t0 = time.time()
    for item in items:
        msgs = item["messages"]
        text = ""
        for m in msgs:
            text += f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n"
        text += "<|im_start|>assistant\n"
        t = tok(text, truncation=True, max_length=MAX_LEN, padding="max_length", return_tensors="pt")
        labels = t["input_ids"].clone()
        labels[t["attention_mask"] == 0] = -100
        encoded.append({
            "input_ids": t["input_ids"].squeeze(),
            "attention_mask": t["attention_mask"].squeeze(),
            "labels": labels.squeeze(),
        })
    log(f"Tokenized {len(encoded)} examples in {time.time()-t0:.0f}s")
    torch.save(encoded, cache_path)
    log("Saved pre-tokenized cache")

gc.collect()
free = os.popen('free -h | grep Mem').read().strip()
log(f"RAM before model: {free}")

# Load model in 4-bit (saves ~1.5GB RAM, prevents OOM)
log("Loading LFM2.5-1.2B-Instruct in 4-bit NF4...")
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import prepare_model_for_kbit_training

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float32,
)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID, quantization_config=bnb_config, device_map="auto",
    trust_remote_code=True,
)
model = prepare_model_for_kbit_training(model)
total_p = sum(p.numel() for p in model.parameters())
log(f"Model loaded — {total_p/1e6:.1f}M params (4-bit NF4)")

gc.collect()
log(f"RAM after model: {os.popen('free -h | grep Mem').read().strip()}")

# LoRA
log("Applying LoRA r=8 on q_proj, v_proj...")
from peft import LoraConfig, get_peft_model, TaskType
lora = LoraConfig(
    task_type=TaskType.CAUSAL_LM, r=LORA_R, lora_alpha=LORA_ALPHA,
    lora_dropout=0.05, target_modules=["q_proj", "v_proj"], bias="none",
)
model = get_peft_model(model, lora)
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
log(f"LoRA applied — {trainable/1e6:.1f}M trainable / {total_p/1e6:.1f}M total")
model.train()
model.config.use_cache = False

gc.collect()
log(f"RAM after LoRA: {os.popen('free -h | grep Mem').read().strip()}")

# Optimizer
optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.01)

# Training
total_steps = len(encoded)
steps_per_epoch = total_steps
log(f"\nTraining: {total_steps} examples x {EPOCHS} epochs, batch={BATCH_SIZE}, max_len={MAX_LEN}")
log(f"  Effective steps: {total_steps // BATCH_SIZE} per epoch")
log("-" * 60)

# Calculate resume point
last_step = get_last_step() if RESUME else 0
start_i = last_step * BATCH_SIZE
if start_i >= total_steps:
    start_i = 0
    last_step = 0
    log("All steps completed in log — starting fresh")

if last_step > 0:
    # Load from last checkpoint
    ckpt_dir = f"jedi_fast_ckpt_step{last_step}"
    if os.path.exists(ckpt_dir):
        from peft import PeftModel
        log(f"Loading checkpoint: {ckpt_dir}")
        model = PeftModel.from_pretrained(model, ckpt_dir)
        model.train()
        log(f"Resumed from step {last_step}")
    else:
        log(f"No checkpoint found at {ckpt_dir}, starting from step {last_step} (data only)")

start = time.time()
global_step = last_step
losses = []

for epoch in range(EPOCHS):
    epoch_loss = 0
    epoch_steps = 0
    i = start_i
    while i < total_steps:
        batch_end = min(i + BATCH_SIZE, total_steps)
        batch = encoded[i:batch_end]
        batch_size = len(batch)

        step_start = time.time()
        ids = torch.stack([b["input_ids"] for b in batch])
        mask = torch.stack([b["attention_mask"] for b in batch])
        lbls = torch.stack([b["labels"] for b in batch])

        out = model(input_ids=ids, attention_mask=mask, labels=lbls)
        loss = out.loss
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        optimizer.zero_grad()

        loss_val = loss.item()
        epoch_loss += loss_val
        losses.append(loss_val)
        global_step += 1
        epoch_steps += 1
        step_time = time.time() - step_start

        if global_step % 10 == 0:
            elapsed = time.time() - start
            steps_done = global_step
            steps_total = (total_steps // BATCH_SIZE) * EPOCHS
            eta = elapsed / steps_done * (steps_total - steps_done)
            examples_processed = global_step * BATCH_SIZE
            pct = 100 * steps_done / steps_total
            log(f"E{epoch+1} step={global_step}/{steps_total} ({pct:.0f}%) loss={loss_val:.4f} step={step_time:.1f}s elapsed={elapsed//60:.0f}m ETA={eta//60:.0f}m examples={examples_processed}")

        if global_step % SAVE_EVERY == 0:
            ckpt_dir = f"jedi_fast_ckpt_step{global_step}"
            model.save_pretrained(ckpt_dir)
            tok.save_pretrained(ckpt_dir)
            log(f"  Checkpoint saved: {ckpt_dir}/")

        i = batch_end

    avg = epoch_loss / epoch_steps
    log(f"Epoch {epoch+1} done — avg_loss={avg:.4f} ({time.time()-start:.0f}s)")

total = time.time() - start
log(f"\n{'='*60}")
log(f"TRAINING COMPLETE — {total:.0f}s ({total/60:.1f}min)")
log(f"{'='*60}")

# Save final
model.save_pretrained("/root/JEDI/jedi_fast_adapter")
tok.save_pretrained("/root/JEDI/jedi_fast_adapter")
log("Final LoRA saved: /root/JEDI/jedi_fast_adapter/")

stats = {
    "model": MODEL_ID,
    "examples": len(encoded),
    "batch_size": BATCH_SIZE,
    "max_len": MAX_LEN,
    "lora_r": LORA_R,
    "total_time_s": total,
    "final_loss": loss_val,
    "epochs": EPOCHS,
}
with open("train_fast_stats.json", "w") as f:
    json.dump(stats, f, indent=2)
log("Stats saved")
log("DONE")
