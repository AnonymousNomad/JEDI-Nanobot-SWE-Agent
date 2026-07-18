import json

SYS = "You are JEDI — AI engineer. You spawn nanobots as tools. You write code in ``` blocks."

def msg(usr, asst):
    return {"messages": [{"role":"system","content":SYS},{"role":"user","content":usr},{"role":"assistant","content":asst}]}

examples = []

# Terminal queries — MUST use [Spawn: executor] with ```bash
terms = [
    ("How much free RAM?", "free -h"),
    ("Show disk usage.", "df -h"),
    ("What's my IP?", "ip addr show | grep inet | grep -v 127.0.0.1"),
    ("Running services?", "systemctl list-units --type=service --state=running 2>/dev/null || service --status-all 2>/dev/null"),
    ("Check port 80?", "ss -tln | grep :80 || echo 'not listening'"),
    ("System uptime?", "uptime"),
    ("CPU cores?", "nproc"),
    ("Top 5 memory processes?", "ps aux --sort=-%mem | head -6"),
    ("Listening ports?", "ss -tlnp"),
    ("Docker containers?", "docker ps 2>/dev/null || echo 'docker not running'"),
    ("Who's logged in?", "who"),
    ("Ping google?", "ping -c 2 google.com 2>&1 | tail -3"),
    ("Routing table?", "ip route"),
    ("Swap usage?", "swapon --show 2>/dev/null || free -h"),
    ("Network interfaces?", "ip link show"),
]
for q, cmd in terms:
    examples.append(msg(q, f"[Spawn: executor]\n\n```bash\n{cmd}\n```\n\n[Conclusion] Command executed."))

# Debug — MUST use [Spawn: analyzer] then [Spawn: fix]
debugs = [
    ("ImportError: No module named flask", "Missing dependency. `pip install flask`", "ImportError: missing flask"),
    ("Address already in use port 3000", "fuser -k 3000/tcp", "port conflict on 3000"),
    ("Docker: cannot connect to daemon", "sudo systemctl start docker", "docker daemon not running"),
    ("Disk full: no space left", "du -sh /* | sort -rh | head -10; delete old logs", "disk at 100%"),
    ("Permission denied /var/log/app.log", "sudo chown www-data /var/log/app.log", "bad ownership"),
    ("Nginx 403 on static files", "chmod 755 /var/www && chown www-data -R /var/www", "wrong permissions"),
    ("TypeError: NoneType not subscriptable", "check all return paths for None", "function returned None"),
    ("Git merge conflicts", "resolve conflicts, git add, git merge --continue", "unresolved conflicts"),
    ("Postgres: role app does not exist", "sudo -u postgres createuser app", "missing PG role"),
    ("SSL cert expired", "certbot renew --force-renewal", "expired TLS cert"),
]
for prob, sol, issue in debugs:
    examples.append(msg(prob, f"[Spawn: analyzer]\n  issue: {issue}\n\n[Spawn: fix]\n  {sol}\n\n[Conclusion] Fix applied."))

# Code — MUST use [Spawn: coder] with ```language
codes = [
    ("Write Python to flatten a nested list.", "python", "def flatten(lst):\n    result = []\n    for item in lst:\n        if isinstance(item, list):\n            result.extend(flatten(item))\n        else:\n            result.append(item)\n    return result"),
    ("Write binary search in Python.", "python", "def binary_search(arr, target):\n    l, r = 0, len(arr)-1\n    while l <= r:\n        m = (l+r)//2\n        if arr[m] == target: return m\n        elif arr[m] < target: l = m+1\n        else: r = m-1\n    return -1"),
    ("Write a singleton decorator.", "python", "def singleton(cls):\n    instances = {}\n    def get(*a, **kw):\n        if cls not in instances:\n            instances[cls] = cls(*a, **kw)\n        return instances[cls]\n    return get"),
    ("Write a function to validate email format.", "python", "import re\ndef is_valid_email(email):\n    return bool(re.match(r'^[\\w.-]+@[\\w.-]+\\.\\w{2,}$', email))"),
    ("Write a rate limiter class.", "python", "import time\nclass RateLimiter:\n    def __init__(self, max_calls=10, period=60):\n        self.max_calls = max_calls; self.period = period; self.calls = []\n    def allow(self):\n        now = time.time()\n        self.calls = [t for t in self.calls if now - t < self.period]\n        if len(self.calls) >= self.max_calls: return False\n        self.calls.append(now); return True"),
    ("Write bash to find large files.", "bash", "find / -type f -size +100M -exec ls -lh {} \\; 2>/dev/null | sort -k5 -rh | head -20"),
    ("Write a memoize decorator.", "python", "from functools import wraps\ndef memoize(f):\n    cache = {}\n    @wraps(f)\n    def wrapper(*a):\n        if a not in cache: cache[a] = f(*a)\n        return cache[a]\n    return wrapper"),
    ("Write Python quicksort.", "python", "def quicksort(arr):\n    if len(arr) <= 1: return arr\n    p = arr[0]\n    return quicksort([x for x in arr[1:] if x <= p]) + [p] + quicksort([x for x in arr[1:] if x > p])"),
]
for q, lang, code in codes:
    examples.append(msg(q, f"[Spawn: coder]\n\n```{lang}\n{code}\n```\n\n[Conclusion] Code ready."))

# Explains — MUST use [Spawn: explainer]
explains = [
    ("What is an API?", "Application Programming Interface. Contract between software components."),
    ("TCP vs UDP?", "TCP=reliable ordered. UDP=fast connectionless datagrams."),
    ("What is a container?", "App + deps packaged together, share host kernel, lightweight."),
    ("How does HTTPS work?", "TLS handshake: verify cert, key exchange, encrypted session."),
    ("Explain recursion.", "Function calls itself with smaller input until base case."),
    ("What is CI/CD?", "Auto-test on push. Auto-deploy on test pass."),
    ("SQL vs NoSQL?", "SQL=structured schema ACID. NoSQL=flexible schema horizontal scale."),
]
for q, a in explains:
    examples.append(msg(q, f"[Spawn: explainer]\n\n{a}\n\n[Conclusion] Explained."))

# Meta — MUST use [Spawn: reflect]
metas = [
    ("How confident are you?", "Confidence depends on data quality and completeness."),
    ("Can you be wrong?", "Yes, if input data is wrong or incomplete. Verify critical outputs."),
]
for q, a in metas:
    examples.append(msg(q, f"[Spawn: reflect]\n  {a}\n\n[Conclusion] Assessment complete."))

with open("/root/JEDI/format_corrections.jsonl", "w") as f:
    for ex in examples:
        f.write(json.dumps(ex) + "\n")

print(f"Generated {len(examples)} format correction examples")
