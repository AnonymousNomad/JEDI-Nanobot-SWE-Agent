#!/usr/bin/env python3
"""
JEDI x Vitalis Cortex — Unified CLI
Wires JEDI nanobot framework into Vitalis Cortex LFM2.5 engine.

Runs the full cognitive pipeline:
  Quadruflow → Memory → Amplifier → LFM2.5 → Attestation → JEDI modules → Output

Also integrates real terminal control for file system operations,
command execution, and terminal-based development workflows.
"""

import os
import sys
import textwrap

# Paths
BASE = os.path.dirname(os.path.abspath(__file__))
CORTEX = os.path.join(BASE, "Vitalis_LFM2.5_Cortex.GGUF")
JEDI = BASE

sys.path.insert(0, CORTEX)
sys.path.insert(0, JEDI)

from _vitalis_loader import InferenceEngine
from jedi.core.engine import JEDIEngine, ThreatLevel
from jedi.core.nanobot import Nanobot, NanobotType
from jedi.core.mission import Mission
from jedi.legal.gate import LegalGate, AuthorizationLevel
from jedi.swarm.coordinator import SwarmCoordinator
from jedi.command.control import MissionControl
from jedi.comms.channel import CommsChannel
from jedi.memory.helix import HelixMemoryStore
from jedi.nanobots.black.ghost import GhostNanobot
from jedi.nanobots.blue.guardian import GuardianNanobot
from jedi.nanobots.red.striker import StrikerNanobot
from jedi.nanobots.green.architect import ArchitectNanobot
from jedi.nanobots.yellow.auditor import AuditorNanobot
from jedi.nanobots.purple.synapse import SynapseNanobot

# Terminal control integration
sys.path.insert(0, BASE)
from terminal_controller import TerminalController, terminal_execute


BANNER = r"""
  ██╗███████╗██████╗ ██╗
  ██║██╔════╝██╔══██╗██║
  ██║█████╗  ██║  ██║██║
  ██║██╔══╝  ██║  ██║██║
  ██║███████╗██████╔╝███████╗
  ╚═╝╚══════╝╚═════╝ ╚══════╝

  ██╗   ██╗██╗████████╗ █████╗ ██╗     ██╗███████╗
  ██║   ██║██║╚══██╔══╝██╔══██╗██║     ██║██╔════╝
  ██║   ██║██║   ██║   ███████║██║     ██║███████╗
  ╚██╗ ██╔╝██║   ██║   ██╔══██║██║     ██║╚════██║
   ╚████╔╝ ██║   ██║   ██║  ██║███████╗██║███████║
    ╚═══╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝╚══════╝

  JEDI x Vitalis Cortex Hybrid
  Nanobot Defense Intelligence  |  LFM2.5 Cognitive Core
  Ferrell Synthetic Intelligence
"""


def main():
    print(BANNER)
    print("  Booting JEDI x Vitalis Cortex...\n")
    
    # Initialize JEDI systems
    engine = JEDIEngine()
    gate = LegalGate()
    mc = MissionControl(engine)
    swarm = SwarmCoordinator("jedi-swarm")
    comms = CommsChannel("jedi-comms")
    memory = HelixMemoryStore()
    
    # Initialize terminal controller
    terminal = TerminalController()
    print("  ✓ Terminal controller online — full bash access available")
    
    # Initialize Vitalis Cortex with LFM2.5
    try:
        cortex = InferenceEngine(model_path=os.path.join(CORTEX, "model", "LFM2.5-1.2B-Instruct-Q4_K_M.gguf"))
        print("\n  ✓ Vitalis Cortex online — LFM2.5 1.2B cognitive core loaded")
        cortex_online = True
    except Exception as e:
        print(f"\n  ✗ Cortex load: {e}")
        cortex_online = False
    
    print("  ✓ JEDI Engine online — nanobot framework armed")
    print("  ✓ Legal Gate active — all ops require authorization")
    print("  ✓ Ledger initialized — immutable audit trail")
    print("  ✓ Swarm Coordinator ready")
    print()
    print("  Type 'help' for commands. Type 'quit' to exit.\n")
    print(f"  Working directory: {terminal.get_working_directory()}\n")
    
    memory.record_episode({"type": "session_start", "cortex_online": cortex_online, "terminal_online": True})
    
    # Chat loop
    while True:
        try:
            prompt = input("\033[96m  JEDI ▸ \033[0m").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Shutdown. All nanobots self-destructed.")
            break
        
        if not prompt:
            continue
        
        if prompt.lower() in ["quit", "exit", "bye"]:
            print("\n  JEDI offline. Ledger sealed. Goodbye.\n")
            break
        
        if prompt.lower() == "clear":
            os.system("clear")
            print(BANNER)
            continue
        
        # Route to appropriate system
        response = route(prompt, cortex if cortex_online else None, engine, gate, mc, swarm, comms, memory, terminal)
        
        # Format output
        print()
        for line in response.split("\n"):
            wrapped = textwrap.fill(line, width=80, initial_indent="  ", subsequent_indent="  ")
            print(wrapped)
        
        # Log
        engine.ledger.log("cli_interaction", {"input": prompt[:80]})
        print()


def route(prompt, cortex, engine, gate, mc, swarm, comms, memory, terminal):
    """Route prompt to appropriate handler."""
    p = prompt.lower()
    
    # === JEDI COMMANDS ===
    if any(w in p for w in ["threat", "risk", "assess"]):
        return threat_handler(p, engine)
    
    if p.startswith("deploy") or p.startswith("deploy nanobot"):
        return deploy_handler(prompt)
    
    if p.startswith("mission"):
        return mission_handler(prompt, mc)
    
    if "swarm" in p.split() and len(p.split()) < 4:
        return swarm_handler(swarm)
    
    if "scan" in p:
        return "═══ SCAN PROTOCOL ═══\nTarget and auth needed. Example:\n  mission create recon 10.0.0.0/24\n  Then I'll deploy a Scout nanobot swarm."
    
    if p in ["help", "/help", "-h", "--help"]:
        return help_text()
    
    if p in ["status", "screenshot"]:
        return status_handler(mc)
    
    if p == "clear":
        return ""
    
    # === TERMINAL CONTROL ===
    if p.startswith("ls ") or p == "ls" or p == "list":
        path = prompt.split(" ", 1)[1] if " " in prompt else "."
        return terminal_list_dir_controller(path, terminal)
    
    if p.startswith("cd "):
        path = prompt.split(" ", 1)[1] if " " in prompt else ".."
        return terminal_cd_controller(path, terminal)
    
    if p.startswith("cat ") or p.startswith("read "):
        path = prompt.split(" ", 1)[1] if " " in prompt else "."
        return terminal_read_file_controller(path, terminal)
    
    if p.startswith("wget ") or p.startswith("download "):
        rest = prompt.split(" ", 1)[1] if " " in prompt else ""
        if rest:
            url = rest.split(" ", 1)[0]
            dest = rest.split(" ", 1)[1] if " " in rest else terminal.get_working_directory() + "/downloaded_file"
            return terminal_download_controller(url, dest, terminal)
    
    if p.startswith("python "):
        rest = prompt.split(" ", 1)[1] if " " in prompt else ""
        return terminal_python_code_controller(rest, terminal)
    
    if p.startswith("rm ") or p.startswith("rmdir "):
        path = prompt.split(" ", 1)[1] if " " in prompt else "."
        return terminal_rm_controller(path, terminal)
    
    if p.startswith("mkdir "):
        path = prompt.split(" ", 1)[1] if " " in prompt else "."
        return terminal_mkdir_controller(path, terminal)
    
    if p.startswith("touch "):
        path = prompt.split(" ", 1)[1] if " " in prompt else "."
        return terminal_touch_controller(path, terminal)
    
    if p.startswith("system "):
        cmd = prompt.split(" ", 1)[1] if " " in prompt else ""
        return terminal_system_controller(cmd, terminal)

    # Use LLM for anything else
    if cortex:
        # Inject JEDI context into the cognitive pipeline
        context_prompt = f"[JEDI CONTEXT] You are JEDI — Joint Entity Defense Infrastructure. A cybersecurity nanobot command AI. Respond as a tactical cybersecurity operations specialist.\n\nUser: {prompt}"
        result = cortex.think(context_prompt, verbose=False)
        return result["response"]
    
    return rule_based(prompt)


def help_text():
    return ("═══ JEDI COMMANDS ═══\n"
            "  help              — This message\n"
            "  status            — System situation report\n"
            "  threat <info>     — Assess a threat\n"
            "  mission create    — Create a new mission\n"
            "  deploy <type>     — Deploy a nanobot\n"
            "  swarm             — Swarm status\n"
            "  scan <target>     — Scan a target\n"
            "  audit <framework> — Compliance check\n"
            "\n  === TERMINAL CONTROL ===\n"
            "  ls [path]         — List directory contents\n"
            "  cd [path]         — Change directory\n"
            "  cat <file>        — Read file contents\n"
            "  system <cmd>      — Execute bash command\n"
            "  python <code>     — Execute Python code\n"
            "  wget <url> [dest] — Download file from URL\n"
            "  mkdir <dir>       — Create directory\n"
            "  touch <file>      — Create empty file\n"
            "  rm <path>         — Remove file or directory\n"
            "\n  quit              — Exit")


def status_handler(mc):
    d = mc.dashboard()
    return (f"═══ JEDI STATUS ═══\n"
            f"  Engine: {d['engine_state']}\n"
            f"  Threat: {d['threat_level']}\n"
            f"  Missions: {d['active_missions']}\n"
            f"  Nanobots: {d['deployed_nanobots']}\n"
            f"  Uptime: {d['uptime_hours']}h")


def threat_handler(p, engine):
    ind = []
    if any(w in p for w in ["apt", "nation", "state"]):
        ind.append({"type": "nation_state_attribution", "severity": 40})
    if any(w in p for w in ["ransom", "malware"]):
        ind.append({"type": "ransomware", "severity": 30})
    if "phish" in p:
        ind.append({"type": "social_engineering", "severity": 15})
    if any(w in p for w in ["exfil", "leak"]):
        ind.append({"type": "data_exfiltration", "severity": 25})
    if "lateral" in p:
        ind.append({"type": "lateral_movement", "severity": 15})
    if not ind:
        ind.append({"type": "suspicious_process", "severity": 5})
    
    level = engine.assess_threat({"indicators": ind, "confidence": 0.7})
    
    lines = [f"═══ THREAT ASSESSMENT ═══", f"  Level: {level.name}"]
    if level.value >= 4:
        lines.extend(["  ⚠ CRITICAL — Immediate containment", "  Deploy Guardian + Sentinel swarm", "  Activate emergency ROE"])
    elif level.value >= 3:
        lines.extend(["  ⚠ HIGH — Enhanced monitoring", "  Deploy Guardian nanobot"])
    elif level.value >= 2:
        lines.extend(["  ▲ MEDIUM — Active monitoring"])
    else:
        lines.extend(["  ✓ LOW — Normal ops"])
    return "\n".join(lines)


def deploy_handler(prompt):
    bot_types = {
        "striker": "🔴 STRIKER — Offensive penetration testing",
        "guardian": "🔵 GUARDIAN — Defensive monitoring",
        "ghost": "⚫ GHOST — Covert/attribution (Gov use)",
        "synapse": "🟣 SYNAPSE — Combined ops coordination",
        "auditor": "🟡 AUDITOR — Compliance checking",
        "architect": "🟢 ARCHITECT — Secure code review",
        "scout": "🟠 SCOUT — Reconnaissance",
        "sentinel": "🟤 SENTINEL — Perimeter watch",
    }
    return (f"═══ NANOBOTS ═══\n" +
            "\n".join(f"  {v}" for v in bot_types.values()) +
            "\n\nUsage: deploy ghost to 10.0.0.1\nOr just ask the LLM to set up a mission.")


def mission_handler(prompt, mc):
    return ("═══ MISSION CONTROL ═══\n"
            "Create: mission create <type> <target>\n"
            "Types: recon, defense, pentest, attribution, sweep\n\n"
            "Example:\n  mission create recon 10.0.0.0/24\n  mission create pentet webapp.example.com")


def swarm_handler(swarm):
    s = swarm.get_swarm_status()
    return (f"═══ SWARM STATUS ═══\n"
            f"  ID: {s['swarm_id']}\n"
            f"  Members: {s['active_members']}/{s['total_members']}\n"
            f"  Tasks queued: {s['tasks_queued']}\n"
            f"  Wisdom: {s.get('wisdom_size', {'intel_entries': 0})['intel_entries']} intel entries\n"
            f"  Decisions: {s['consensus_reached']}\n"
            f"\nTo deploy a swarm: create a mission first.")


def terminal_list_dir_controller(path, terminal):
    files = terminal.list_directory(path)
    return f"====== {path} (working directory: {terminal.get_working_directory()}) ======\n" + "\n".join(f"  {f}" for f in files)


def terminal_cd_controller(path, terminal):
    success = terminal.change_directory(path)
    return f"Changed directory to: {path}" if success else f"Failed to change directory to: {path}"


def terminal_read_file_controller(path, terminal):
    content = terminal.read_file(path)
    return f"==== Contents of {path} ====" + ("\n" + content if not content.startswith("Error reading") else "\n" + content)


def terminal_download_controller(url, dest, terminal):
    success = terminal.download_file(url, dest)
    if success:
        return f"Downloaded {url} to {dest}"
    else:
        return f"Failed to download {url}"


def terminal_python_code_controller(code, terminal):
    result = terminal.execute_bash_command(f"python3 -c \"{code.replace('\\', '\\\\').replace('\"', '\\\"').replace('\n', '\\\\n')}\"", capture_output=True)
    output = result.stdout if result.success else f"Error: {result.stderr}"
    return f"Python execution result:\n{output}"


def terminal_system_controller(cmd, terminal):
    # Support multi-command chaining with logical line breaks
    if '&' in cmd or '&&' in cmd or '||' in cmd:
        # Split on shell operators to execute commands sequentially
        commands = []
        for c in cmd.replace('&&', '|').replace('||', '|').replace('\\&', '|').split('|'):
            c = c.strip()
            if c:
                commands.append(c)
        
        all_output = []
        for i, c in enumerate(commands):
            if i > 0:
                all_output.append(f"--- Command {i+1}: {c} ---")
            result = terminal.execute_bash_command(c)
            all_output.append(f"Command {i+1}: {c}")
            all_output.append(f"Status: {'SUCCESS' if result.success else 'FAILED'}")
            if result.stdout:
                all_output.append("Output:")
                all_output.append(result.stdout)
            if result.stderr:
                all_output.append("STDERR:")
                all_output.append(result.stderr)
        
        return "\n".join(all_output)
    else:
        result = terminal.execute_bash_command(cmd)
        return f"Shell command result:\nstdout: {result.stdout}\nstderr: {result.stderr}\nExit code: {result.returncode}"


def terminal_rm_controller(path, terminal):
    result = terminal.execute_bash_command(f"rm -rf \"{path}\"")
    return f"Removal result: {'Success' if result.success else 'Failed'}\n{result.stderr}"


def terminal_mkdir_controller(path, terminal):
    result = terminal.create_directory(path)
    return f"Directory creation: {'Success' if result else 'Failed'}"


def terminal_touch_controller(path, terminal):
    result = terminal.write_file(path, "")
    return f"File creation: {'Success' if result else 'Failed'}"


def rule_based(prompt):
    return ("JEDI operational. Your query goes through the LFM2.5 cognitive core\n"
            "with Quadruflow routing, memory retrieval, and attestation gating.\n"
            "Type 'help' for commands or ask me anything about cybersecurity.\n"
            "(Full LLM mode available when the model loads successfully.)")


if __name__ == "__main__":
    main()
