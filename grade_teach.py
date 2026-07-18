#!/usr/bin/env python3
"""Round 2: Test trained adapter, grade, create corrections, train"""
import os, sys, json, time, gc
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import torch
torch.set_num_threads(8)

ROUND = sys.argv[1] if len(sys.argv) > 1 else "2"
LOG_FILE = f"grade_teach_r{ROUND}.log"
def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f: f.write(line + "\n")

log("=" * 60)
log(f"JEDI Grade & Teach — Round {ROUND}")
log("=" * 60)

MODEL_ID = "LiquidAI/LFM2.5-1.2B-Instruct"
ADAPTER_PATH = "/root/JEDI/jedi_fast_adapter"

# Load test bank
with open("/root/JEDI/test_bank.json") as f:
    tests = json.load(f)
log(f"Loaded {len(tests)} test questions")

# Load model with adapter for inference
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

tok = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True, local_files_only=True)
tok.pad_token = tok.eos_token

log("Loading model with adapter for testing...")
if os.path.exists(ADAPTER_PATH):
    # Use 4-bit to keep memory low (only need inference)
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float32)
    base = AutoModelForCausalLM.from_pretrained(MODEL_ID, quantization_config=bnb, device_map="auto", trust_remote_code=True, local_files_only=True)
    model = PeftModel.from_pretrained(base, ADAPTER_PATH)
    model.eval()
    log("Loaded trained adapter")
else:
    log("No adapter found, using base model")
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float32)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, quantization_config=bnb, device_map="auto", trust_remote_code=True, local_files_only=True)
    model.eval()

# Generate answers
log("\n--- Generating Answers ---")
results = []
for t in tests:
    prompt = f"<|im_start|>system\nYou are JEDI — expert in terminal, SWE, security, architecture. Answer precisely and completely.<|im_end|>\n<|im_start|>user\n{t['question']}<|im_end|>\n<|im_start|>assistant\n"
    inputs = tok(prompt, return_tensors="pt", truncation=True, max_length=512)
    t0 = time.time()
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.3, do_sample=True, pad_token_id=tok.eos_token_id, repetition_penalty=1.1)
    answer = tok.decode(outputs[0], skip_special_tokens=True)
    if "<|im_start|>assistant" in answer:
        answer = answer.split("<|im_start|>assistant")[-1].strip()
    if answer.startswith("\n"):
        answer = answer[1:]
    results.append({**t, "model_answer": answer})
    log(f"  [{t['id']}] Generated ({len(answer)} chars) in {time.time()-t0:.0f}s")

# Grade
log("\n--- Grading ---")
corrections = []
for r in results:
    al = r["model_answer"].lower()
    expected = r["expected_elements"]
    found = sum(1 for e in expected if e.lower() in al)
    score = found / len(expected)
    r["score"] = score
    log(f"  [{r['id']}] score={score:.0%} ({found}/{len(expected)}) {r['domain']}")
    if score < 0.7:
        corrections.append(r)

log(f"\n{len(corrections)}/{len(results)} need correction")

# Compare with previous round
try:
    with open(f"/root/JEDI/test_results_r1.json") as f:
        prev = json.load(f)
    prev_scores = {p["id"]: p["score"] for p in prev}
    improved = sum(1 for r in results if r["score"] > prev_scores.get(r["id"], 0))
    declined = sum(1 for r in results if r["score"] < prev_scores.get(r["id"], 0))
    log(f"Round 1 → Round 2: {improved} improved, {declined} declined")
except: pass

# Save results
with open(f"/root/JEDI/test_results_r{ROUND}.json", "w") as f:
    json.dump(results, f, indent=2)

# Create correction data
log("\n--- Creating Training Data ---")
examples = []
for c in corrections:
    examples.append({
        "messages": [
            {"role": "system", "content": "You are JEDI — expert across all technical domains."},
            {"role": "user", "content": c["question"]},
            {"role": "assistant", "content": c["correct_answer"]},
        ]
    })
    # Reflection example
    examples.append({
        "messages": [
            {"role": "system", "content": "You are JEDI — learn from mistakes."},
            {"role": "user", "content": f"What was wrong with my answer to: {c['question']}?"},
            {"role": "assistant", "content": f"Missing elements: {', '.join(c['expected_elements'])}. Correct approach: {c['correct_answer']}"},
        ]
    })

corr_path = f"/root/JEDI/correction_data_r{ROUND}.jsonl"
with open(corr_path, "w") as f:
    for ex in examples:
        f.write(json.dumps(ex) + "\n")
log(f"Created {len(examples)} correction examples")

# Train on corrections + previous corrections (accumulate knowledge)
log("\n--- Fine-Tuning ---")
all_examples = examples[:]
for prev_round in range(1, int(ROUND)):
    prev_path = f"/root/JEDI/correction_data_r{prev_round}.jsonl"
    if os.path.exists(prev_path):
        with open(prev_path) as f:
            for line in f:
                if line.strip():
                    all_examples.append(json.loads(line))
log(f"Training on {len(all_examples)} total examples (new + previous rounds)")

# Switch to float16 for fast training
del model, base
gc.collect()

from transformers import AutoModelForCausalLM as M2
from peft import LoraConfig, get_peft_model

tok2 = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True, local_files_only=True)
tok2.pad_token = tok2.eos_token

log("Loading float16 model for training...")
t0 = time.time()
model = M2.from_pretrained(MODEL_ID, dtype=torch.float16, device_map="cpu", low_cpu_mem_usage=True, trust_remote_code=True, local_files_only=True)
log(f"Loaded in {time.time()-t0:.0f}s")

lora = LoraConfig(task_type="CAUSAL_LM", r=8, lora_alpha=16, lora_dropout=0.05, target_modules=["q_proj","v_proj"], bias="none")
model = get_peft_model(model, lora)
model.train()
model.config.use_cache = False

# Tokenize
MAX_LEN = 256
encoded = []
for ex in all_examples:
    text = ""
    for m in ex["messages"]:
        text += f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n"
    text += "<|im_start|>assistant\n"
    t = tok2(text, truncation=True, max_length=MAX_LEN, padding="max_length", return_tensors="pt")
    labels = t["input_ids"].clone()
    labels[t["attention_mask"] == 0] = -100
    encoded.append({"input_ids": t["input_ids"].squeeze(), "attention_mask": t["attention_mask"].squeeze(), "labels": labels.squeeze()})

optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=2e-4)
BATCH_SIZE = 2
EPOCHS = 2
total = len(encoded)
steps_total = ((total - 1) // BATCH_SIZE) + 1
log(f"Training: {total} examples x {EPOCHS} epochs")

start = time.time()
for epoch in range(EPOCHS):
    eloss = 0; steps = 0; i = 0
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
        optimizer.step(); optimizer.zero_grad()
        del out, ids, mask, lbls, batch
        eloss += lv; steps += 1; i = be
        log(f"  E{epoch+1} step={steps}/{steps_total} loss={lv:.4f} step_t={time.time()-t0:.1f}s")
        if steps % 10 == 0: gc.collect()
    log(f"  Epoch {epoch+1} avg_loss={eloss/steps:.4f}")

model.save_pretrained(ADAPTER_PATH)
tok2.save_pretrained(ADAPTER_PATH)
log(f"Adapter saved to {ADAPTER_PATH}")
log(f"Total: {time.time()-start:.0f}s")
log("DONE")
