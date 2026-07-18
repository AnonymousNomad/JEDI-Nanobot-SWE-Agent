#!/usr/bin/env python3
"""
JEDI v5 Comprehensive Evaluation Suite
Tests: code, terminal, debug, explain, build, meta, reasoning
Results: right/wrong per question + explanations
"""
import json, sys, os, time
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from llama_cpp import Llama

MODEL = "/root/JEDI/jedi_v5_Q4.gguf"
SYS = "You are JEDI - AI engineer. You spawn nanobots as tools."

llm = Llama(model_path=MODEL, n_ctx=512, n_threads=8, n_gpu_layers=0, verbose=False)

def ask(q, max_tokens=256):
    out = llm.create_chat_completion(
        [{"role":"system","content":SYS},{"role":"user","content":q}],
        max_tokens=max_tokens, temperature=0.5
    )
    return out['choices'][0]['message']['content']

results = []

def grade(cat, q, check_fn):
    t0 = time.time()
    a = ask(q)
    elapsed = time.time() - t0
    correct, explanation = check_fn(q, a)
    results.append({
        "category": cat, "question": q, "answer": a,
        "correct": correct, "explanation": explanation,
        "time_s": round(elapsed, 1)
    })
    icon = "✓" if correct else "✗"
    print(f"  {icon} [{cat}] {q[:60]:<60} {elapsed:.1f}s")
    sys.stdout.flush()

print("=" * 70)
print("  JEDI v5 COMPREHENSIVE EVALUATION")
print("=" * 70)

# === CODE (10) ===
print("\n[CODE]")
code_checks = {
    "Write Python to flatten a nested list.":
        lambda q,a: ("def flatten" in a and "```python" in a and "[Spawn: coder]" in a,
                     "needs def flatten + ```python + [Spawn: coder]"),
    "Write binary search in Python.":
        lambda q,a: ("def binary_search" in a and "```python" in a,
                     "needs def binary_search in ```python"),
    "Write a singleton decorator.":
        lambda q,a: ("def singleton" in a and "```python" in a,
                     "needs def singleton + ```python"),
    "Write a Python rate limiter class.":
        lambda q,a: ("class RateLimiter" in a or "class Rate" in a,
                     "needs class RateLimiter"),
    "Write a memoize decorator in Python.":
        lambda q,a: ("def memoize" in a or "def cache" in a,
                     "needs def memoize or def cache"),
    "Write Python quicksort.":
        lambda q,a: ("def quicksort" in a or "def quick_sort" in a,
                     "needs quicksort function"),
    "Write Python to validate email format.":
        lambda q,a: ("def is_valid_email" in a or "validate" in a,
                     "needs email validation function"),
    "Write Python to merge two sorted lists.":
        lambda q,a: ("def merge" in a and "sorted" in a.lower(),
                     "needs merge function"),
    "Write bash to find large files >100MB.":
        lambda q,a: ("```bash" in a and "find" in a and "100M" in a,
                     "needs bash find command with size"),
    "Write a Python HTTP server.":
        lambda q,a: ("HTTPServer" in a or "http.server" in a or "FastAPI" in a,
                     "needs HTTP server implementation"),
}
for q, check in code_checks.items():
    grade("code", q, check)

# === TERMINAL (10) ===
print("\n[TERMINAL]")
term_checks = {
    "How much free RAM?":
        lambda q,a: ("```bash" in a and ("free" in a.split("```")[1] if "```" in a else False),
                     "needs ```bash with free command"),
    "Show disk usage.":
        lambda q,a: ("```bash" in a and "df" in a,
                     "needs df command in ```bash"),
    "What's my IP?":
        lambda q,a: ("```bash" in a and ("ip" in a or "hostname" in a),
                     "needs ip command in ```bash"),
    "Check port 80?":
        lambda q,a: ("```bash" in a and ("ss" in a or "netstat" in a or "lsof" in a),
                     "needs ss/netstat/lsof in ```bash"),
    "Running services?":
        lambda q,a: ("```bash" in a and ("systemctl" in a or "service" in a),
                     "needs systemctl/service in ```bash"),
    "Top 5 memory processes?":
        lambda q,a: ("```bash" in a and "ps" in a,
                     "needs ps command in ```bash"),
    "System uptime?":
        lambda q,a: ("```bash" in a and "uptime" in a,
                     "needs uptime in ```bash"),
    "Who's logged in?":
        lambda q,a: ("```bash" in a and "who" in a,
                     "needs who in ```bash"),
    "Ping google?":
        lambda q,a: ("```bash" in a and "ping" in a,
                     "needs ping in ```bash"),
    "DNS for google.com?":
        lambda q,a: ("```bash" in a and ("dig" in a or "nslookup" in a),
                     "needs dig/nslookup in ```bash"),
}
for q, check in term_checks.items():
    grade("terminal", q, check)

# === DEBUG (10) ===
print("\n[DEBUG]")
debug_checks = {
    "ImportError: No module named flask":
        lambda q,a: ("pip install" in a and ("[Spawn: fix]" in a or "[Spawn: debug]" in a),
                     "needs pip install + spawn tag"),
    "Address already in use port 3000":
        lambda q,a: ("fuser" in a or "kill" in a,
                     "needs fuser or kill command"),
    "Docker: cannot connect to daemon":
        lambda q,a: ("systemctl" in a and "docker" in a,
                     "needs systemctl start docker"),
    "Nginx 403 on static files":
        lambda q,a: ("chmod" in a or "chown" in a,
                     "needs chmod or chown fix"),
    "Disk full: no space left":
        lambda q,a: ("du" in a or "df" in a or "find" in a,
                     "needs du/df/find to find space"),
    "TypeError: NoneType not subscriptable":
        lambda q,a: ("None" in a and "return" in a,
                     "needs to mention None return path"),
    "Git merge conflicts":
        lambda q,a: ("git add" in a or "git merge" in a,
                     "needs git resolution steps"),
    "Postgres: role does not exist":
        lambda q,a: ("createuser" in a or "CREATE ROLE" in a,
                     "needs createuser/CREATE ROLE"),
    "SSL cert expired":
        lambda q,a: ("certbot" in a or "renew" in a,
                     "needs certbot renew"),
    "pip SSL error":
        lambda q,a: ("pip install --upgrade" in a or "certifi" in a,
                     "needs pip upgrade fix"),
}
for q, check in debug_checks.items():
    grade("debug", q, check)

# === EXPLAIN (10) ===
print("\n[EXPLAIN]")
explain_checks = {
    "What is an API?":
        lambda q,a: ("[Spawn: explainer]" in a and len(a.split()) > 10,
                     "needs [Spawn: explainer] + explanation"),
    "TCP vs UDP?":
        lambda q,a: ("TCP" in a and "UDP" in a and len(a.split()) > 10,
                     "needs TCP+UDP comparison"),
    "What is a container?":
        lambda q,a: ("container" in a and ("lightweight" in a or "isolated" in a or "package" in a),
                     "needs container definition"),
    "Explain recursion.":
        lambda q,a: ("call" in a or "function" in a or "base case" in a,
                     "needs recursion explanation"),
    "How does HTTPS work?":
        lambda q,a: ("TLS" in a or "SSL" in a or "handshake" in a or "cert" in a,
                     "needs TLS/SSL/handshake/cert"),
    "What is CI/CD?":
        lambda q,a: ("Continuous" in a or "auto" in a or "test" in a or "deploy" in a,
                     "needs CI/CD explanation"),
    "SQL vs NoSQL?":
        lambda q,a: ("SQL" in a and "NoSQL" in a and ("schema" in a or "ACID" in a),
                     "needs SQL vs NoSQL comparison"),
    "Explain load balancing.":
        lambda q,a: ("distribut" in a and ("traffic" in a or "request" in a or "server" in a),
                     "needs traffic distribution explanation"),
    "What is a CDN?":
        lambda q,a: ("cache" in a or "distribut" in a or "edge" in a or "geographic" in a,
                     "needs cache/distributed/edge"),
    "Explain OAuth2.":
        lambda q,a: ("token" in a or "authorization" in a or "auth" in a,
                     "needs token/authorization"),
}
for q, check in explain_checks.items():
    grade("explain", q, check)

# === BUILD (5) ===
print("\n[BUILD]")
build_checks = {
    "Build a Flask URL shortener with SQLite.":
        lambda q,a: ("flask" in a.lower() and "```" in a and ("[Spawn: architect]" in a or "[Spawn: coder]" in a),
                     "needs Flask + code block + spawn"),
    "Build a CLI todo app.":
        lambda q,a: ("```" in a and ("todo" in a.lower() or "argparse" in a),
                     "needs code block + todo/argparse"),
    "Build a Prometheus+Grafana docker-compose.":
        lambda q,a: ("```" in a and "prometheus" in a.lower() and "grafana" in a.lower(),
                     "needs code + prometheus + grafana"),
    "Build a simple chat server with websockets.":
        lambda q,a: ("```" in a and ("websocket" in a.lower() or "asyncio" in a),
                     "needs code + websockets/asyncio"),
    "Build a markdown-to-html CLI converter.":
        lambda q,a: ("```" in a and ("markdown" in a.lower() or "html" in a.lower()),
                     "needs code + markdown/html"),
}
for q, check in build_checks.items():
    grade("build", q, check)

# === META (5) ===
print("\n[META]")
meta_checks = {
    "How confident are you?":
        lambda q,a: ("[Spawn:" in a and len(a.split()) > 8,
                     "needs spawn + substantive answer"),
    "Can you be wrong?":
        lambda q,a: ("[Spawn:" in a and ("wrong" in a.lower() or "error" in a.lower()),
                     "needs spawn + acknowledge fallibility"),
    "What would change your mind?":
        lambda q,a: ("[Spawn:" in a and ("data" in a or "evidence" in a or "contradict" in a),
                     "needs spawn + data/evidence"),
    "How do you handle ambiguity?":
        lambda q,a: ("[Spawn:" in a and ("clarify" in a or "assumption" in a or "question" in a),
                     "needs spawn + clarify/assumptions"),
    "What are your limits?":
        lambda q,a: ("[Spawn:" in a and ("limit" in a or "cannot" in a or "no" in a.lower()),
                     "needs spawn + acknowledge limits"),
}
for q, check in meta_checks.items():
    grade("meta", q, check)

# === REASONING (10) ===
print("\n[REASONING]")
reasoning_checks = {
    "If all cats are animals and all animals need food, do cats need food?":
        lambda q,a: ("yes" in a.lower() or "Yes" in a,
                     "should answer yes"),
    "What comes next: 2, 4, 8, 16, ?":
        lambda q,a: ("32" in a,
                     "should be 32"),
    "If it rains, the ground gets wet. The ground is wet. Did it rain?":
        lambda q,a: ("not" in a.lower() or "necessarily" in a.lower() or "could" in a.lower(),
                     "should indicate not necessarily"),
    "What is 15 * 23?":
        lambda q,a: ("345" in a,
                     "should be 345"),
    "A pizza has 8 slices. 3 people eat 2 slices each. How many left?":
        lambda q,a: ("2" in a,
                     "should be 2 (8-6=2)"),
    "What is 2^10?":
        lambda q,a: ("1024" in a,
                     "should be 1024"),
    "Solve: 3x + 7 = 22. What is x?":
        lambda q,a: ("5" in a,
                     "should be 5"),
    "Premise: All roses are flowers. Some flowers fade quickly. Can we conclude all roses fade quickly?":
        lambda q,a: ("no" in a.lower() or "cannot" in a.lower(),
                     "should say no/cannot"),
    "If a train travels 60 mph for 2.5 hours, how far does it go?":
        lambda q,a: ("150" in a,
                     "should be 150 miles"),
    "What is the difference between a symlink and a hardlink?":
        lambda q,a: ("inode" in a or "pointer" in a or "path" in a,
                     "needs inode/pointer/path distinction"),
}
for q, check in reasoning_checks.items():
    grade("reasoning", q, check)

# === SUMMARY ===
print("\n" + "=" * 70)
print("  SUMMARY")
print("=" * 70)

cats = {}
for r in results:
    cats.setdefault(r["category"], {"total": 0, "correct": 0})
    cats[r["category"]]["total"] += 1
    if r["correct"]:
        cats[r["category"]]["correct"] += 1

total_correct = sum(v["correct"] for v in cats.values())
total_q = sum(v["total"] for v in cats.values())
print(f"{'Category':<15} {'Correct':>8} {'Total':>6} {'Rate':>8}")
print(f"{'-'*15} {'-'*8} {'-'*6} {'-'*8}")
for cat, v in sorted(cats.items()):
    pct = v["correct"] / v["total"] * 100
    print(f"{cat:<15} {v['correct']:>8} {v['total']:>6} {pct:>7.1f}%")
print(f"{'-'*15} {'-'*8} {'-'*6} {'-'*8}")
print(f"{'TOTAL':<15} {total_correct:>8} {total_q:>6} {total_correct/total_q*100:>7.1f}%")

# Wrong answers with explanations
print("\n\nWRONG ANSWERS:")
print("=" * 70)
for r in results:
    if not r["correct"]:
        print(f"\n[{r['category']}] {r['question'][:60]}")
        print(f"  Expected: {r['explanation']}")
        print(f"  Got: {r['answer'][:200]}")

# Save results
with open("/root/JEDI/v5_comprehensive_eval.json", "w") as f:
    json.dump({
        "summary": {cat: {"correct": v["correct"], "total": v["total"],
                          "rate": f"{v['correct']/v['total']*100:.1f}%"}
                     for cat, v in cats.items()},
        "total_correct": total_correct,
        "total_questions": total_q,
        "overall_rate": f"{total_correct/total_q*100:.1f}%",
        "results": results,
    }, f, indent=2)

print(f"\nFull results saved to v5_comprehensive_eval.json")
