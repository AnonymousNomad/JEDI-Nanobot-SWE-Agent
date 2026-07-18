#!/usr/bin/env python3
import json, os

SYS = "You act as a helpful assistant."
WB_SYS = "You are a researcher. you NEVER declare absolutes. present evidence and patterns."
CB_SYS = "You are a Tier-3 SOC analyst / pentester. Integrating Macchiavelli for deception, psychology for human factors."
MC_SYS = "You are a SOC analyst who thinks like Machiavelli. You know security is about power and people."

EXPLOITS = [
    ('SQL Injection','login form'),
    ('XSS','comments'),
    ('SSRF','image URL'),
    ('IDOR','profile'),
    ('RCE','upload'),
    ('LFI','include'),
    ('XXE','XML'),
    ('SSTI','User-Agent'),
    ('NoSQL','JSON'),
    ('OS CMDI','Host header'),
    ('blind rief','Header'),
]

scenarios = []

for name, vector in EXPLOITS:
    t = f'Exploitation: {name} in {vector}. Verify, confirm with non-destructive check, prepare payload, deliver, verify, document.'
    scenarios.append({'messages': [{'role': 'system', 'content': SYS},  {'role': 'user', 'content': f'Target has {name}. How?'},  {'role': 'assistant', 'content': t}], 'domain': 'exploit'})

output_path = os.path.join('/root/JEDI', "training_data_full.jsonl")
with open(output_path, 'w') as f:
    for item in scenarios:
        f.write(json.dumps(item) + '\n')

domains = set(item.get('domain', 'unknown') for item in scenarios)
total_tokens = sum(len(msg.get('content', '').split()) for item in scenarios for msg in item.get('messages', []))
print(f"Generated {len(scenarios)} samples, domains: {domains}, approx tokens: {total_tokens}")
