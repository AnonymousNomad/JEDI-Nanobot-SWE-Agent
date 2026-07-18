#!/usr/bin/env python3
"""
JEDI Terminal Agent — interactive CLI with autonomous command execution.
Hybrid approach: intent matching for common tasks + model reasoning for complex ones.
"""
import os, sys, time, re, subprocess, signal, readline, json, shlex
from pathlib import Path
from datetime import datetime

os.environ["TOKENIZERS_PARALLELISM"] = "false"

MODEL_PATH = os.path.expanduser("/root/JEDI/jedi_v5_Q4.gguf")
MAX_TOKENS = 200
N_CTX = 2048
N_THREADS = 8

C = {
    "reset": "\033[0m", "bold": "\033[1m", "dim": "\033[2m",
    "prompt": "\033[38;5;141m", "cmd": "\033[38;5;81m",
    "output": "\033[38;5;120m", "jedi": "\033[38;5;218m",
    "error": "\033[38;5;196m", "info": "\033[38;5;244m",
    "system": "\033[38;5;208m", "title": "\033[38;5;228m",
}

SYSTEM_PROMPT = """You are JEDI — expert across all technical domains. You spawn nanobot swarms to solve problems. Nanobots communicate through shared state. Swarm intelligence emerges from their coordination.

You have full terminal access. When a command result is provided, analyze it with:
[Spawn: type]
  state: key=value
  key insights...

Then conclude with [Conclusion].

Example flow:
User: "What OS?"
You: [Spawn: scan size=1K]
  state: os=Linux, arch=aarch64
[Conclusion] Linux on ARM aarch64.

Never make up data. Analyze what you're given. If no data is available, say so honestly."""

HISTORY_FILE = os.path.expanduser("~/.jedi_history")
MAX_HISTORY = 500

# ── Intent → Command mappings ──
INTENTS = {
    "os": {"patterns": ["what os", "which os", "operating system", "what linux", "what distro", "uname"],
            "cmd": "uname -a", "timeout": 5},
    "ram": {"patterns": ["how much ram", "memory", "mem", "free -h", "ram usage", "memory usage"],
            "cmd": "free -h", "timeout": 5},
    "disk": {"patterns": ["disk", "storage", "space", "df -h", "disk usage", "how much space"],
            "cmd": "df -h /", "timeout": 5},
    "cpu": {"patterns": ["cpu", "processor", "load average", "uptime", "nproc"],
            "cmd": "nproc && cat /proc/loadavg", "timeout": 5},
    "ip": {"patterns": ["ip address", "what's my ip", "network", "ifconfig", "ip addr"],
            "cmd": "ip addr show | grep inet | grep -v 127.0.0.1 | head -3", "timeout": 5},
    "processes": {"patterns": ["process", "running", "ps aux", "top", "ps -"],
            "cmd": "ps aux --sort=-%mem | head -10", "timeout": 5},
    "ports": {"patterns": ["port", "listening", "ss -", "netstat", "open port"],
            "cmd": "ss -tlnp | head -15", "timeout": 5},
    "who": {"patterns": ["who's logged", "logged in", "who", "users", "w "],
            "cmd": "who && w", "timeout": 5},
    "date": {"patterns": ["what time", "current time", "date", "what day"],
            "cmd": "date '+%Y-%m-%d %H:%M:%S %Z'", "timeout": 5},
    "pwd": {"patterns": ["where am i", "current directory", "pwd", "what dir"],
            "cmd": "pwd && ls -la", "timeout": 5},
    "git_status": {"patterns": ["git status", "git diff", "repo status"],
            "cmd": "cd /root/JEDI && git status --short 2>/dev/null || echo 'not a git repo'", "timeout": 5},
    "env": {"patterns": ["environment", "env", "path", "printenv", "what's set"],
            "cmd": "echo PATH=$PATH\\nSHELL=$SHELL\\nHOME=$HOME\\nUSER=$USER", "timeout": 5},
}


class JEDI:
    def __init__(self):
        from llama_cpp import Llama
        self.llm = Llama(MODEL_PATH, n_ctx=N_CTX, n_threads=N_THREADS, verbose=False)
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.exec_count = 0
        self.cmd_outputs = {}
        self.load_history()

    def load_history(self):
        try: readline.read_history_file(HISTORY_FILE)
        except FileNotFoundError: pass
        readline.set_history_length(MAX_HISTORY)

    def save_history(self):
        try: readline.write_history_file(HISTORY_FILE)
        except: pass

    def log(self, tag, msg, color="info"):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"{C['dim']}[{ts}]{C['reset']} {color}{C['bold']}{tag}{C['reset']} {msg}")

    def build_prompt(self):
        text = ""
        for msg in self.messages:
            role, content = msg["role"], msg["content"]
            text += f"<|im_start|>{role}\n{content}<|im_end|>\n"
        text += "<|im_start|>assistant\n"
        return text

    def detect_intent(self, text):
        text_lower = text.lower().strip()
        for intent_name, intent in INTENTS.items():
            for pat in intent["patterns"]:
                if pat in text_lower:
                    return intent_name, intent["cmd"], intent["timeout"]
        return None, None, None

    def execute_cmd(self, cmd, timeout=30):
        self.exec_count += 1
        cmd_id = f"#{self.exec_count}"
        self.log(cmd_id, C['cmd'] + cmd, "cmd")
        try:
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            out = proc.stdout + proc.stderr
            if proc.returncode != 0:
                out += f"\n[exit: {proc.returncode}]"
        except subprocess.TimeoutExpired:
            out = f"[timeout {timeout}s]"
        except Exception as e:
            out = f"[error: {e}]"
        self.cmd_outputs[cmd_id] = out
        if out.strip():
            for line in out.rstrip().split("\n")[:15]:
                self.log(cmd_id, C['output'] + line, "output")
            if len(out.split("\n")) > 15:
                self.log(cmd_id, f"... ({len(out.split(chr(10)))} lines total)", "info")
        return out

    def generate(self):
        prompt = self.build_prompt()
        t0 = time.time()
        out = self.llm(prompt, max_tokens=MAX_TOKENS, temperature=0.5,
                        stop=["<|im_end|>"], echo=False)
        resp = out["choices"][0]["text"].strip()
        self.log("took", f"{time.time()-t0:.0f}s", "info")
        return resp

    def parse_and_exec(self, text):
        """Look for code blocks or EXEC blocks in model output and execute them."""
        # Markdown code blocks
        blocks = re.findall(r'```(?:bash|sh|shell)?\s*\n(.*?)\n```', text, re.DOTALL)
        if not blocks:
            blocks = re.findall(r'\[EXEC\](.*?)\[/EXEC\]', text, re.DOTALL)
        cmds = [b.strip() for b in blocks if b.strip()
                and not b.strip().startswith('Spawn')
                and len(b.strip()) > 2]
        results = []
        for cmd in cmds:
            r = self.execute_cmd(cmd, timeout=15)
            results.append((cmd, r))
        return results

    def clean_response(self, resp):
        resp = re.sub(r'```(?:bash|sh|shell)?\s*\n.*?\n```', '', resp, flags=re.DOTALL)
        resp = re.sub(r'\[EXEC\].*?\[/EXEC\]', '', resp)
        resp = re.sub(r'\n{3,}', '\n\n', resp).strip()
        return resp

    def run(self):
        print(f"\n{C['title']}{C['bold']}╔══════════════════════════════════════╗")
        print(f"║      JEDI Terminal Agent v2          ║")
        print(f"║   Talk naturally — I run commands    ║")
        print(f"║   Type 'exit' to quit.               ║")
        print(f"╚══════════════════════════════════════╝{C['reset']}\n")

        while True:
            try:
                user_input = input(f"\n{C['prompt']}{C['bold']}▸ {C['reset']}")
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not user_input.strip(): continue
            if user_input.lower() in ("exit", "quit"): break
            if user_input.lower() == "reset":
                self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                print(f"{C['info']}Session reset.{C['reset']}")
                continue

            readline.add_history(user_input)
            self.log("user", user_input, "prompt")

            # Step 1: Check for known intents → run command directly
            intent_name, intent_cmd, intent_timeout = self.detect_intent(user_input)
            if intent_cmd:
                self.log("auto", f"[{intent_name}] → {intent_cmd}", "system")
                result = self.execute_cmd(intent_cmd, intent_timeout)
                # Send both the result and the original question to model for analysis
                self.messages.append({
                    "role": "user",
                    "content": f"{user_input}\n\n[System info from `{intent_cmd}`]\n{result}\n\nAnalyze these results."
                })
            else:
                # Step 2: Unknown intent → ask the model
                self.messages.append({"role": "user", "content": user_input})

            # Step 3: Model generates response (analyzes results or figures out what to do)
            resp = self.generate()

            # Step 4: Check if model outputs any commands in its response
            exec_results = self.parse_and_exec(resp)
            cleaned = self.clean_response(resp)

            if cleaned:
                print(f"\n{C['jedi']}{cleaned}{C['reset']}")

            # Step 5: Feed back any executed command results
            for cmd, result in exec_results:
                self.messages.append({"role": "assistant", "content": resp})
                self.messages.append({
                    "role": "user",
                    "content": f"[Result of: {cmd}]\n{result}\n[Continue analysis.]"
                })
                # Generate analysis of results
                resp2 = self.generate()
                cleaned2 = self.clean_response(resp2)
                if cleaned2:
                    print(f"\n{C['jedi']}{cleaned2}{C['reset']}")
                resp = resp2  # chain for message tracking

            # Store the final assistant response
            if not exec_results:  # didn't get stored above
                self.messages.append({"role": "assistant", "content": resp})

            # Trim conversation to last 20 messages to keep context manageable
            if len(self.messages) > 22:
                self.messages = [self.messages[0]] + self.messages[-20:]

        self.save_history()


if __name__ == "__main__":
    JEDI().run()
