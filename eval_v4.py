from llama_cpp import Llama
import json

model = Llama(
    model_path='/root/JEDI/jedi_v4_Q4.gguf',
    n_ctx=512,
    n_threads=8,
    n_gpu_layers=0,
    verbose=False,
)

tests = {
    "terminal": [
        "How much free RAM?",
        "Show disk usage.",
        "What's my IP?",
        "Running services?",
        "Check port 80?",
        "Top 5 memory processes?",
        "System uptime?",
        "CPU cores?",
        "Docker containers?",
        "Listening ports?",
    ],
    "debug": [
        "ImportError: No module named flask",
        "Permission denied /var/log/app.log",
        "Address already in use port 3000",
        "Docker: cannot connect to daemon",
        "Nginx 403 on static files",
        "TypeError: NoneType not subscriptable",
        "Disk full: no space left",
        "Postgres: role app does not exist",
        "Git merge conflicts in main.py",
        "SSL cert expired for example.com",
    ],
    "explain": [
        "What is an API?",
        "TCP vs UDP?",
        "What is a container?",
        "Explain recursion.",
        "SQL vs NoSQL?",
        "How does HTTPS work?",
        "What is CI/CD?",
        "Explain load balancing.",
        "What is a CDN?",
        "Explain OAuth2.",
    ],
    "code": [
        "Write Python to flatten a nested list.",
        "Write a Python function to validate email format.",
        "Write a Python rate limiter class.",
        "Write a function to merge two sorted lists.",
        "Write binary search in Python.",
        "Write Python quicksort.",
        "Write a singleton decorator in Python.",
        "Write a memoize/cache decorator.",
        "Write a Python function to extract URLs from text.",
        "Write a bash script to find large files.",
    ],
    "build": [
        "Build a Flask URL shortener with SQLite.",
        "Build a CLI todo app.",
        "Build a Prometheus+Grafana docker-compose.",
        "Build a markdown-to-html CLI converter.",
        "Build a simple chat server with websockets.",
    ],
    "meta": [
        "How confident are you?",
        "What are your limits?",
        "Can you be wrong?",
        "What would change your mind?",
        "How do you handle ambiguity?",
    ],
}

results = {}
for cat, prompts in tests.items():
    cat_results = []
    for q in prompts:
        messages = [
            {"role": "system", "content": "You are JEDI - AI engineer. You spawn nanobots as tools."},
            {"role": "user", "content": q},
        ]
        out = model.create_chat_completion(messages, max_tokens=256, temperature=0.5)
        text = out['choices'][0]['message']['content']
        spawn = '[Spawn:' in text
        conclusion = '[Conclusion]' in text
        code = '```' in text
        quality = 'good' if spawn and conclusion else ('partial' if spawn else 'poor')
        cat_results.append({
            "q": q[:60],
            "spawn": spawn, "conclusion": conclusion, "code": code,
            "quality": quality,
        })
    spawn_rate = sum(1 for r in cat_results if r["spawn"]) / len(cat_results) * 100
    conc_rate = sum(1 for r in cat_results if r["conclusion"]) / len(cat_results) * 100
    code_rate = sum(1 for r in cat_results if r["code"]) / len(cat_results) * 100
    results[cat] = {
        "count": len(cat_results),
        "spawn_rate": spawn_rate,
        "conclusion_rate": conc_rate,
        "code_rate": code_rate,
    }
    print(f"\n{'='*50}")
    print(f"{cat.upper()}: {len(cat_results)} questions")
    print(f"  Spawn: {spawn_rate:.0f}%  Conclusion: {conc_rate:.0f}%  Code: {code_rate:.0f}%")
    for r in cat_results:
        icon = '✓' if r['quality'] == 'good' else '~'
        print(f"  {icon} Spawn={r['spawn']} Conc={r['conclusion']} Code={r['code']} | {r['q'][:50]}")

print(f"\n{'='*50}")
print("SUMMARY")
total_q = sum(v['count'] for v in results.values())
total_spawn = sum(v['count'] * v['spawn_rate']/100 for v in results.values()) / total_q * 100
total_conc = sum(v['count'] * v['conclusion_rate']/100 for v in results.values()) / total_q * 100
total_code = sum(v['count'] * v['code_rate']/100 for v in results.values()) / total_q * 100
print(f"Overall: {total_q} questions")
print(f"  Spawn Rate: {total_spawn:.0f}%")
print(f"  Conclusion Rate: {total_conc:.0f}%")
print(f"  Code Rate: {total_code:.0f}%")

with open('/root/JEDI/v4_eval.json', 'w') as f:
    json.dump({"results": results, "summary": {
        "total": total_q, "spawn_rate": total_spawn,
        "conclusion_rate": total_conc, "code_rate": total_code
    }}, f, indent=2)
print("Saved to v4_eval.json")
