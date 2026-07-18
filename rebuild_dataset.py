import json

# Read the 22 correction examples from existing train_29.jsonl
corrections = []
with open('/root/JEDI/train_29.jsonl') as f:
    for i, line in enumerate(f):
        if i >= 22:
            break
        corrections.append(json.loads(line))

# Read the 7 new personality examples
new_examples = []
with open('/root/JEDI/new_nanobot.jsonl') as f:
    for line in f:
        new_examples.append(json.loads(line))

# Combine: 22 corrections + 7 personality = 29
combined = corrections + new_examples

with open('/root/JEDI/train_29.jsonl', 'w') as f:
    for ex in combined:
        f.write(json.dumps(ex) + '\n')

total = sum(1 for _ in open('/root/JEDI/train_29.jsonl'))
print(f'Wrote {total} examples (22 corrections + 7 personality)')

# Rough token estimate (4 chars per token for English)
for i, ex in enumerate(combined):
    text = json.dumps(ex)
    est_tokens = len(text) // 4
    if est_tokens > 250:
        print(f'  [{i}] ~{est_tokens} tokens (WARNING: near/blows MAX_LEN=256)')
    elif est_tokens > 200:
        print(f'  [{i}] ~{est_tokens} tokens')
