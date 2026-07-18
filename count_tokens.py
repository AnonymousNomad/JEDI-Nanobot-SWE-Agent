import json, os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from transformers import AutoTokenizer

MODEL_ID = "/root/.cache/huggingface/hub/models--LiquidAI--LFM2.5-1.2B-Instruct/snapshots/868df74dd56ff8a0c2ac5dbf281690c2dbebe4c9"
tok = AutoTokenizer.from_pretrained(MODEL_ID, local_files_only=True)

# Read old train_29.jsonl
with open('/root/JEDI/train_29.jsonl') as f:
    old_examples = [json.loads(line) for line in f]

# Read new examples
with open('/root/JEDI/new_nanobot.jsonl') as f:
    new_examples = [json.loads(line) for line in f]

MAX_LEN = 256

print("=== OLD TRAIN_29 EXAMPLES ===")
for i, ex in enumerate(old_examples):
    text = ""
    for m in ex["messages"]:
        text += f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n"
    text += "<|im_start|>assistant\n"
    t = tok(text, truncation=False)
    n = len(t["input_ids"])
    flag = "OVER" if n > MAX_LEN else "OK"
    print(f"  [{i:2d}] {n:4d} tokens [{flag}]  role_last={ex['messages'][-1]['role']}")

print(f"\n=== NEW EXAMPLES ===")
for i, ex in enumerate(new_examples):
    text = ""
    for m in ex["messages"]:
        text += f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n"
    text += "<|im_start|>assistant\n"
    t = tok(text, truncation=False)
    n = len(t["input_ids"])
    flag = "OVER" if n > MAX_LEN else "OK"
    print(f"  [{i:2d}] {n:4d} tokens [{flag}]")

# Test combined
combined = old_examples[:22] + new_examples
print(f"\n=== COMBINED (22 corrections + {len(new_examples)} new) ===")
over = [(i, n) for i, ex in enumerate(combined) for n in [len(tok(
    "".join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in ex["messages"]) + "<|im_start|>assistant\n",
    truncation=False
)["input_ids"])] if n > MAX_LEN]
if over:
    print(f"  {len(over)} examples OVER {MAX_LEN} tokens:")
    for i, n in over:
        print(f"    [{i}] {n} tokens")
else:
    print("  All examples fit within MAX_LEN=256")
    print(f"  Max: {max(len(tok(''.join(f'<|im_start|>{m[\"role\"]}\n{m[\"content\"]}<|im_end|>\n' for m in ex['messages']) + '<|im_start|>assistant\n', truncation=False)['input_ids']) for ex in combined)}")
    print(f"  Min: {min(len(tok(''.join(f'<|im_start|>{m[\"role\"]}\n{m[\"content\"]}<|im_end|>\n' for m in ex['messages']) + '<|im_start|>assistant\n', truncation=False)['input_ids']) for ex in combined)}")
    print(f"  Avg: {sum(len(tok(''.join(f'<|im_start|>{m[\"role\"]}\n{m[\"content\"]}<|im_end|>\n' for m in ex['messages']) + '<|im_start|>assistant\n', truncation=False)['input_ids']) for ex in combined)/len(combined):.0f}")
