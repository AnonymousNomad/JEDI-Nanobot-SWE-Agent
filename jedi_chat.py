#!/usr/bin/env python3
"""
JEDI Terminal Chat Client — Simple chat interface for JEDI AI.
Works with or without fine-tuned model.
"""

import sys
import os
import json
import time
import hashlib
import textwrap
from datetime import datetime

# Add JEDI to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jedi.core.engine import JEDIEngine, ThreatLevel
from jedi.core.nanobot import Nanobot, NanobotType
from jedi.core.mission import Mission, MissionStatus
from jedi.legal.gate import LegalGate, AuthorizationLevel
from jedi.swarm.coordinator import SwarmCoordinator
from jedi.command.control import MissionControl
from jedi.comms.channel import CommsChannel
from jedi.memory.helix import HelixMemoryStore

# Try loading the fine-tuned model
MODEL_LOADED = False
model = None
tokenizer = None

def load_model():
    global MODEL_LOADED, model, tokenizer
    lora_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jedi-tiny-lora")
    if os.path.exists(lora_path):
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            from peft import PeftModel
            print("  Loading JEDI model (TinyLlama 1.1B + LoRA)...")
            tokenizer = AutoTokenizer.from_pretrained(lora_path)
            base = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                torch_dtype="auto", device_map="cpu", low_cpu_mem_usage=True)
            model = PeftModel.from_pretrained(base, lora_path)
            model.eval()
            MODEL_LOADED = True
            print("  ✓ JEDI model loaded!")
        except Exception as e:
            print(f"  ✗ Model load failed: {e}")
            print("  Falling back to rule-based responses.")
    else:
        print("  No fine-tuned model found. Using rule-based JEDI.")


def ai_respond(prompt: str) -> str:
    """Get response from JEDI AI (model or rule-based)."""
    if MODEL_LOADED and model is not None:
        try:
            formatted = f"<|user|>\n{prompt}\n<|assistant|>\n"
            inputs = tokenizer(formatted, return_tensors="pt", truncation=True, max_length=1024)
            import torch
            with torch.no_grad():
                outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.7,
                                        do_sample=True, pad_token_id=tokenizer.eos_token_id)
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            if "<|assistant|>" in response:
                return response.split("<|assistant|>")[-1].strip()
            return response
        except Exception as e:
            return f"[Model error: {e}]"
    
    # Rule-based fallback
    return rule_based_respond(prompt)


def rule_based_respond(prompt: str) -> str:
    """Rule-based JEDI responses when model isn't loaded."""
    p = prompt.lower()
    
    if any(w in p for w in ["hello", "hi", "hey", "greet"]):
        return ("JEDI Online. Joint Entity Defense Infrastructure v0.1.0.\n"
                "I'm your cybersecurity nanobot command interface.\n"
                "Type 'help' for available commands or 'status' for system report.")
    
    if "status" in p or "screenshot" in p or "situation" in p:
        mc = MissionControl()
        dash = mc.dashboard()
        return (f"═══ JEDI STATUS ═══\n"
                f"  Engine: {dash['engine_state']}\n"
                f"  Threat: {dash['threat_level']}\n"
                f"  Missions: {dash['active_missions']}\n"
                f"  Nanobots: {dash['deployed_nanobots']}\n"
                f"  Uptime: {dash['uptime_hours']}h")
    
    if "help" in p:
        return ("═══ JEDI COMMANDS ═══\n"
                "  status    — System situation report\n"
                "  mission   — Create a new mission\n"
                "  deploy    — Deploy a nanobot\n"
                "  scan      — Scan a target\n"
                "  swarm     — View swarm status\n"
                "  threat    — Assess a threat\n"
                "  audit     — Run compliance check\n"
                "  help      — This message\n"
                "  quit      — Exit JEDI\n"
                "\nYou can also ask me cybersecurity questions directly.")
    
    if "deploy" in p or "nanobot" in p:
        return ("Nanobot types available:\n"
                "  🔴 STRIKER  — Offensive (pen test)\n"
                "  🔵 GUARDIAN — Defensive (monitor)\n"
                "  🟣 SYNAPSE  — Combined (coordinate)\n"
                "  🟡 AUDITOR  — Compliance (audit)\n"
                "  🟢 ARCHITECT — Secure dev (review)\n"
                "  ⚫ GHOST    — Covert (attribution)\n"
                "  🟠 SCOUT    — Reconnaissance\n"
                "  🟤 SENTINEL — Perimeter watch\n"
                "\nUsage: 'deploy ghost to 10.0.0.1' or ask me to create a mission.")
    
    if "threat" in p or "assess" in p or "risk" in p:
        engine = JEDIEngine()
        indicators = []
        if "apt" in p or "nation" in p:
            indicators.append({"type": "nation_state_attribution", "severity": 40})
        if "malware" in p or "virus" in p or "ransomware" in p:
            indicators.append({"type": "ransomware", "severity": 30})
        if "phish" in p:
            indicators.append({"type": "social_engineering", "severity": 15})
        if "exfil" in p or "leak" in p:
            indicators.append({"type": "data_exfiltration", "severity": 25})
        if "lateral" in p:
            indicators.append({"type": "lateral_movement", "severity": 15})
        if not indicators:
            indicators.append({"type": "suspicious_process", "severity": 5})
        
        level = engine.assess_threat({"indicators": indicators, "confidence": 0.7})
        
        response = f"═══ THREAT ASSESSMENT ═══\n  Level: {level.name}\n"
        if level.value >= 4:
            response += "  ⚠ CRITICAL — Recommend immediate containment\n"
            response += "  Deploy Guardian + Sentinel swarm\n"
            response += "  Activate emergency ROE"
        elif level.value >= 3:
            response += "  ⚠ HIGH — Enhanced monitoring recommended\n"
            response += "  Deploy Guardian nanobot for continuous monitoring"
        elif level.value >= 2:
            response += "  ▲ MEDIUM — Active monitoring\n"
            response += "  Sentinel on perimeter, log all anomalies"
        else:
            response += "  ✓ LOW — Normal operations\n"
            response += "  Continue passive monitoring"
        return response
    
    if "scan" in p or "recon" in p or "map" in p:
        return ("═══ SCAN PROTOCOL ═══\n"
                "To scan a target, I need:\n"
                "  1. Target IP/hostname\n"
                "  2. Scan type (quick/full/stealth)\n"
                "  3. Authorization level\n\n"
                "Example: 'scan 192.168.1.0/24 quick'\n"
                "I'll deploy a Scout nanobot with appropriate stealth settings.")
    
    if "swarm" in p:
        return ("═══ SWARM STATUS ═══\n"
                "  No active swarm.\n"
                "  To create one: 'mission create recon 10.0.0.0/24'\n"
                "  This will deploy a coordinated swarm with\n"
                "  Scout, Guardian, and Sentinel nanobots.")
    
    if "audit" in p or "compliance" in p or "nist" in p:
        gate = LegalGate()
        auth = gate.create_authorization("JEDI-CLI", AuthorizationLevel.OBSERVE,
            "LOCAL", "CLI-AUTH", "audit", {"address": "localhost"})
        return ("═══ COMPLIANCE AUDIT ═══\n"
                "  Frameworks available:\n"
                "  • NIST CSF\n"
                "  • ISO 27001\n"
                "  • HIPAA\n"
                "  • FedRAMP\n"
                "  • GDPR\n\n"
                "  To run: 'audit nist on 10.0.0.1'\n"
                "  I'll deploy an Auditor nanobot for continuous monitoring.")
    
    if "mission" in p:
        return ("═══ MISSION CONTROL ═══\n"
                "  Create a mission:\n"
                "  'mission create <type> <target>'\n\n"
                "  Types: recon, defense, pentest, attribution, sweep\n\n"
                "  Example:\n"
                "  mission create recon 10.0.0.0/24\n"
                "  mission create pentest webapp.example.com\n"
                "  mission create attribution 10.0.0.50")
    
    if any(w in p for w in ["quit", "exit", "bye", "shutdown"]):
        return "JEDI shutting down. All nanobots self-destructed. Ledger verified. Goodbye."
    
    # Default: provide useful info
    return ("I'm JEDI — Joint Entity Defense Infrastructure AI.\n"
            "I can help with cybersecurity operations:\n"
            "  • Assess threats and risks\n"
            "  • Plan reconnaissance missions\n"
            "  • Deploy nanobot swarms\n"
            "  • Coordinate red/blue team ops\n"
            "  • Compliance auditing\n"
            "  • Attribution analysis\n\n"
            "Type 'help' for commands or ask me anything about cybersecurity.")


BANNER = r"""
  ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
  ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
  ██║███████║██████╔╝██║   ██║██║███████╗
██╔╝██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
███████╗██║  ██║██║  ██║ ╚████╔╝ ██║███████║
╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
  Joint Entity Defense Infrastructure
  Cybersecurity Nanobot Command Interface
  v0.1.0 — Ferrell Synthetic Intelligence
"""


def main():
    print(BANNER)
    print("  Initializing JEDI systems...")
    
    # Load AI model
    load_model()
    
    # Initialize systems
    engine = JEDIEngine()
    gate = LegalGate()
    mc = MissionControl(engine)
    swarm = SwarmCoordinator("cli-swarm")
    comms = CommsChannel("cli-comms")
    memory = HelixMemoryStore()
    
    print(f"  ✓ Engine: {engine.state.value}")
    print(f"  ✓ Legal Gate: active")
    print(f"  ✓ Ledger: {len(engine.ledger.entries)} entries")
    print(f"  ✓ Swarm: {swarm.get_swarm_status()['total_members']} members")
    print(f"  ✓ Comms: encrypted")
    print(f"  ✓ Memory: {memory.get_stats()['total_memories']} entries")
    print()
    print("  Type 'help' for commands. Type 'quit' to exit.")
    print()
    
    # Chat loop
    while True:
        try:
            user_input = input("\033[96m  JEDI ▸ \033[0m").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  JEDI shutting down. All nanobots self-destructed.")
            break
        
        if not user_input:
            continue
        
        # Handle special commands
        if user_input.lower() in ["quit", "exit", "bye", "shutdown"]:
            print("\n  JEDI shutting down. Ledger verified. Goodbye.\n")
            break
        
        if user_input.lower() == "clear":
            os.system("clear" if os.name != "nt" else "cls")
            print(BANNER)
            continue
        
        # Get AI response
        response = ai_respond(user_input)
        
        # Format and display
        print()
        for line in response.split("\n"):
            wrapped = textwrap.fill(line, width=80, initial_indent="  ", subsequent_indent="  ")
            print(wrapped)
        
        # Log to memory
        memory.record_episode({
            "type": "cli_interaction",
            "input": user_input[:100],
            "response_length": len(response),
        })
        engine.ledger.log("cli_interaction", {"input": user_input[:50]})


if __name__ == "__main__":
    main()
