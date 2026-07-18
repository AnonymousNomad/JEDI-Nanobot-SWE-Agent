import json, os
from transformers import AutoTokenizer

MODEL_ID = "/root/.cache/huggingface/hub/models--LiquidAI--LFM2.5-1.2B-Instruct/snapshots/868df74dd56ff8a0c2ac5dbf281690c2dbebe4c9"
DATA_PATH = "/root/JEDI/comprehensive_v4.jsonl"

tok = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True, local_files_only=True)
tok.pad_token = tok.eos_token

examples = []
with open(DATA_PATH) as f:
    for line in f:
        if line.strip():
            examples.append(json.loads(line))

max_len = 0
for ex in examples:
    text = ""
    for m in ex["messages"]:
        text += f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n"
    text += "<|im_start|>assistant\n"
    t = tok(text, truncation=False)
    if len(t["input_ids"]) > max_len:
        max_len = len(t["input_ids"])

print(f"Max token length: {max_len}")
print(f"Total examples: {len(examples)}")

# Distribution
lens = []
for ex in examples:
    text = ""
    for m in ex["messages"]:
        text += f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n"
    text += "<|im_start|>assistant\n"
    t = tok(text, truncation=False)
    lens.append(len(t["input_ids"]))

import statistics
print(f"Mean: {statistics.mean(lens):.0f}, Median: {statistics.median(lens):.0f}, Max: {max(lens)}, Min: {min(lens)}")
print(f"Over 256: {sum(1 for l in lens if l > 256)}/{len(lens)}")
print(f"Over 512: {sum(1 for l in lens if l > 512)}/{len(lens)}")
print(f"Over 1024: {sum(1 for l in lens if l > 1024)}/{len(lens)}")
