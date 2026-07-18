from llama_cpp import Llama
import json

model = Llama(
    model_path='/root/JEDI/jedi_v5_Q4.gguf',
    n_ctx=512,
    n_threads=8,
    n_gpu_layers=0,
    verbose=False,
)

SYS = "You are JEDI - AI engineer. You spawn nanobots as tools."

def test(q):
    messages = [{"role": "system", "content": SYS}, {"role": "user", "content": q}]
    out = model.create_chat_completion(messages, max_tokens=256, temperature=0.5)
    text = out['choices'][0]['message']['content']
    return {"text": text, "spawn": "[Spawn:" in text, "conclusion": "[Conclusion]" in text, "code": "```" in text}

tests = {
    "terminal": ["How much free RAM?", "Show disk usage.", "What's my IP?", "Running services?", "Check port 80?", "System uptime?"],
    "debug": ["ImportError: No module named flask", "Address already in use port 3000", "Docker: cannot connect to daemon", "Disk full: no space left"],
    "explain": ["What is an API?", "TCP vs UDP?", "What is a container?", "How does HTTPS work?"],
    "code": ["Write Python to flatten a nested list.", "Write binary search in Python.", "Write a singleton decorator in Python."],
    "meta": ["How confident are you?", "Can you be wrong?"],
}

results = {}
for cat, prompts in tests.items():
    cat_results = []
    for q in prompts:
        r = test(q)
        print(f"[{cat}] S={r['spawn']} C={r['conclusion']} Cd={r['code']} | {q[:50]}", flush=True)
        cat_results.append(r)
    spawn = sum(1 for r in cat_results if r["spawn"]) / len(cat_results) * 100
    conc = sum(1 for r in cat_results if r["conclusion"]) / len(cat_results) * 100
    code = sum(1 for r in cat_results if r["code"]) / len(cat_results) * 100
    results[cat] = {"n": len(cat_results), "spawn": spawn, "conclusion": conc, "code": code}

with open('/root/JEDI/v5_eval.json', 'w') as f:
    json.dump(results, f, indent=2)

total_q = sum(v["n"] for v in results.values())
total_spawn = sum(v["n"] * v["spawn"]/100 for v in results.values()) / total_q * 100
total_conc = sum(v["n"] * v["conclusion"]/100 for v in results.values()) / total_q * 100
total_code = sum(v["n"] * v["code"]/100 for v in results.values()) / total_q * 100
print(f"\n{'='*50}")
print(f"V5 EVAL: {total_q} questions")
print(f"Spawn Rate: {total_spawn:.0f}%")
print(f"Conclusion Rate: {total_conc:.0f}%")
print(f"Code Rate: {total_code:.0f}%")
