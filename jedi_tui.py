#!/usr/bin/env python3
"""
JEDI Terminal Operations Center
Cybersecurity defense interface with network maps, threat dashboards, 
and live status panels. Cyberpunk meets SOC.
"""
import sys, os, time, json, threading, hashlib
from datetime import datetime
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "Vitalis_LFM2.5_Cortex.GGUF"))

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.live import Live
from rich.align import Align
from rich.rule import Rule
from rich import box

console = Console()

# ─── COLOR SCHEME ──────────────────────────────────────────────
C = {
    "bg": "#0a0e17",
    "cyan": "#00d4ff",
    "green": "#00ff88",
    "red": "#ff3366",
    "yellow": "#ffcc00",
    "orange": "#ff8800",
    "purple": "#aa66ff",
    "gray": "#445566",
    "dim": "#334455",
    "white": "#ddeeff",
    "dark": "#0d1117",
}

# ─── ASCII ART ─────────────────────────────────────────────────
LOGO = """[bold cyan]
 ███╗   ██╗███████╗██████╗ ██╗     ███████╗ █████╗ ███████╗██╗  ██╗
 ████╗  ██║██╔════╝██╔══██╗██║     ██╔════╝██╔══██╗██╔════╝██║ ██╔╝
 ██╔██╗ ██║█████╗  ██║  ██║██║     █████╗  ███████║███████╗█████╔╝ 
 ██║╚██╗██║██╔══╝  ██║  ██║██║     ██╔══╝  ██╔══██║╚════██║██╔═██╗ 
 ██║ ╚████║███████╗██████╔╝███████╗███████╗██║  ██║███████║██║  ██╗
 ╚═╝  ╚═══╝╚══════╝╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝[/]

[bold white]  JOINT ENTITY DEFENSE INFRASTRUCTURE — OPERATIONS CENTER[/]
[dim]  Vitalis Cortex Hybrid | LFM2.5 1.2B | FSI[/]"""

THREAT_MAP = """[bold cyan]┌──────────────────────────────────────────────────────────────────────┐
│                     NETWORK TOPOLOGY — LIVE MAP                       │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│    [dim]10.0.0.0/24[/]                 [dim]172.16.0.0/16[/]              │
│                                                                      │
│   ┌─────────┐              ┌─────────┐      ┌─────────┐             │
│   │ [green]DC-01[/]   │──────────│ [yellow]WEB-01[/]  │──────│ [yellow]WEB-02[/]  │             │
│   │ Domain  │    ▲        │ Nginx   │      │ Apache  │             │
│   │ Control │    │        │ :80/:443│      │ :80/:443│             │
│   └────┬────┘    │        └────┬────┘      └────┬────┘             │
│        │         │             │                │                   │
│   ┌────┴────┐    │        ┌────┴────┐      ┌────┴────┐             │
│   │ [green]FILE-01[/] │    │        │ [yellow]DB-01[/]   │      │ [red]HONEYPOT[/] │             │
│   │ SMB/NFS │    │        │ MySQL   │      │ 🍯 Trap │             │
│   │ :445    │    │        │ :3306   │      │ :22     │             │
│   └─────────┘    │        └─────────┘      └────┬────┘             │
│                  │                              │                   │
│             [bold red]◆ GHOST-01[/]                  │                   │
│             [dim]nanobot active[/]                 │                   │
│                  │                              │                   │
│   ┌─────────┐    │        ┌─────────┐      ┌────┴────┐             │
│   │ [cyan]SENT-01[/] │────┘        │ [yellow]APP-01[/]  │      │ [green]BACKUP[/] │             │
│   │ Sentinel│              │ API Srv │      │ Offsite │             │
│   │ :8080   │              │ :8443   │      │ :9090   │             │
│   └─────────┘              └─────────┘      └─────────┘             │
│                                                                      │
│  [dim]Legend: [green]■ Secure[/] [yellow]■ Monitor[/] [red]■ Threat[/] [cyan]◆ Active Bot[/] 🍯 Honeypot[/]  │
└──────────────────────────────────────────────────────────────────────┘[/]"""


class JEDITerminal:
    def __init__(self):
        self.engine = None
        self.jedi_engine = None
        self.status = "INITIALIZING"
        self.threat_level = "NONE"
        self.active_bots = []
        self.missions = []
        self.alerts = deque(maxlen=20)
        self.logs = deque(maxlen=50)
        self.network_nodes = self._init_network()
        self.start_time = time.time()
        self._init_engines()
    
    def _init_network(self):
        return [
            {"name": "DC-01", "ip": "10.0.0.10", "type": "domain_controller", "status": "secure", "services": ["AD DS", "DNS", "Kerberos"]},
            {"name": "FILE-01", "ip": "10.0.0.20", "type": "file_server", "status": "secure", "services": ["SMB", "NFS"]},
            {"name": "WEB-01", "ip": "10.0.0.30", "type": "web_server", "status": "monitor", "services": ["Nginx", "SSL"]},
            {"name": "WEB-02", "ip": "10.0.0.31", "type": "web_server", "status": "monitor", "services": ["Apache", "SSL"]},
            {"name": "DB-01", "ip": "10.0.0.40", "type": "database", "status": "monitor", "services": ["MySQL"]},
            {"name": "APP-01", "ip": "10.0.0.50", "type": "app_server", "status": "monitor", "services": ["API", "REST"]},
            {"name": "SENT-01", "ip": "10.0.0.100", "type": "sentinel", "status": "active", "services": ["Monitor", "IDS"]},
            {"name": "BACKUP", "ip": "10.0.0.200", "type": "backup", "status": "secure", "services": ["Offsite"]},
            {"name": "HONEYPOT", "ip": "172.16.0.5", "type": "honeypot", "status": "active", "services": ["SSH Trap"]},
        ]
    
    def _init_engines(self):
        try:
            from _vitalis_loader import InferenceEngine
            model = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                "Vitalis_LFM2.5_Cortex.GGUF/model/LFM2.5-1.2B-Instruct-Q4_K_M.gguf")
            self.engine = InferenceEngine(model_path=model)
            from jedi.core.engine import JEDIEngine
            self.jedi_engine = JEDIEngine()
            self.status = "ONLINE"
            self.add_alert("SYSTEM", "All systems operational. Cortex loaded.", "info")
        except Exception as e:
            self.status = "DEGRADED"
            self.add_alert("SYSTEM", f"Engine load failed: {e}", "error")
    
    def add_alert(self, source, msg, level="info"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.alerts.append({"ts": ts, "source": source, "msg": msg, "level": level})
    
    def add_log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[dim]{ts}[/] {msg}")
    
    def uptime(self):
        secs = int(time.time() - self.start_time)
        m, s = divmod(secs, 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    # ─── PANEL RENDERERS ────────────────────────────────────────
    def render_header(self):
        return Panel(Align.center(LOGO, vertical="middle"), 
                     style="bold cyan", box=box.DOUBLE)
    
    def render_status_bar(self):
        uptime = self.uptime()
        threat_color = {"NONE": "green", "LOW": "green", "MEDIUM": "yellow", 
                       "HIGH": "orange", "CRITICAL": "red", "NATION_STATE": "bold red"}
        tc = threat_color.get(self.threat_level, "white")
        
        status_color = "green" if self.status == "ONLINE" else "yellow" if self.status == "DEGRADED" else "red"
        
        bar = Table(box=None, show_header=False, show_edge=False, padding=(0,1))
        bar.add_column(style="dim")
        bar.add_column()
        bar.add_column(style="dim")
        bar.add_column()
        bar.add_column(style="dim")
        bar.add_column()
        bar.add_column(style="dim")
        bar.add_column()
        
        bar.add_row(
            "STATUS", f"[{status_color}]{self.status}[/]",
            "THREAT", f"[{tc}]{self.threat_level}[/]",
            "BOTS", f"[cyan]{len(self.active_bots)}[/]",
            "UPTIME", f"[white]{uptime}[/]",
        )
        return Panel(bar, title="[bold]SYSTEM STATUS[/]", border_style="cyan", box=box.ROUNDED)
    
    def render_network_map(self):
        table = Table(title="[bold cyan]NETWORK TOPOLOGY — LIVE MAP[/]", box=box.SIMPLE_HEAVY,
                     border_style="cyan", show_lines=False)
        table.add_column("NODE", style="bold", width=10)
        table.add_column("IP", width=15, style="dim")
        table.add_column("TYPE", width=18)
        table.add_column("STATUS", width=12)
        table.add_column("SERVICES", width=30)
        
        status_style = {
            "secure": "[bold green]■ SECURE[/]",
            "monitor": "[yellow]■ MONITOR[/]", 
            "threat": "[bold red]■ THREAT[/]",
            "active": "[cyan]◆ ACTIVE[/]",
        }
        
        for node in self.network_nodes:
            table.add_row(
                node["name"],
                node["ip"],
                node["type"].replace("_", " ").title(),
                status_style.get(node["status"], node["status"]),
                ", ".join(node["services"]),
            )
        
        return Panel(table, title="[bold]INFRASTRUCTURE[/]", border_style="cyan", box=box.ROUNDED)
    
    def render_threat_panel(self):
        threat_bar = Text()
        levels = ["NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL", "NATION_STATE"]
        colors = ["green", "green", "yellow", "orange", "red", "bold red"]
        current_idx = levels.index(self.threat_level) if self.threat_level in levels else 0
        
        for i, (level, color) in enumerate(zip(levels, colors)):
            if i <= current_idx:
                threat_bar.append(f" {level[:3].upper()} ", style=f"bold {color} on {color}")
            else:
                threat_bar.append(f" {level[:3].upper()} ", style=f"dim white on grey15")
            threat_bar.append(" ")
        
        threat_bar.append(f"\n\n  Level: ", style="dim")
        threat_bar.append(self.threat_level, style=f"bold {colors[current_idx]}")
        
        desc = {
            "NONE": "Normal operations. No active threats detected.",
            "LOW": "Elevated monitoring. Suspicious activity observed.",
            "MEDIUM": "Active monitoring. Anomaly detected, investigation needed.",
            "HIGH": "Enhanced posture. Confirmed threat, containment recommended.",
            "CRITICAL": "Immediate response required. Active compromise detected.",
            "NATION_STATE": "Maximum alert. Nation-state level threat confirmed.",
        }
        threat_bar.append(f"\n  {desc.get(self.threat_level, '')}", style="dim")
        
        return Panel(threat_bar, title="[bold]THREAT LEVEL[/]", border_style="cyan", box=box.ROUNDED)
    
    def render_agents_panel(self):
        table = Table(box=box.SIMPLE_HEAVY, border_style="cyan", show_header=True)
        table.add_column("BOT ID", style="bold cyan", width=16)
        table.add_column("TYPE", width=10)
        table.add_column("STATE", width=12)
        table.add_column("MISSION", width=20)
        table.add_column("UPTIME", width=10)
        
        if not self.active_bots:
            table.add_row("[dim]No active bots[/]", "", "", "", "")
        else:
            for bot in self.active_bots:
                table.add_row(
                    bot["id"],
                    bot["type"],
                    f"[green]{bot['state']}[/]",
                    bot.get("mission", "—"),
                    bot.get("uptime", "0s"),
                )
        
        return Panel(table, title="[bold]DEPLOYED NANOBOTS[/]", border_style="cyan", box=box.ROUNDED)
    
    def render_alerts_panel(self):
        table = Table(box=None, show_header=False, border_style="cyan")
        table.add_column(width=8, style="dim")
        table.add_column(width=10, style="bold")
        table.add_column(width=50)
        
        level_style = {"info": "[cyan]INFO[/]", "warn": "[yellow]WARN[/]", 
                      "error": "[red]ERROR[/]", "crit": "[bold red]CRIT[/]"}
        
        alerts = list(self.alerts)[-8:]
        if not alerts:
            table.add_row("[dim]—", "", "No recent alerts[/]")
        else:
            for a in alerts:
                table.add_row(
                    a["ts"],
                    level_style.get(a["level"], a["level"]),
                    a["msg"][:50],
                )
        
        return Panel(table, title="[bold]ALERT FEED[/]", border_style="cyan", box=box.ROUNDED)
    
    def render_missions_panel(self):
        table = Table(box=box.SIMPLE_HEAVY, border_style="cyan")
        table.add_column("MISSION", style="bold", width=18)
        table.add_column("TYPE", width=10)
        table.add_column("STATUS", width=12)
        table.add_column("BOTS", width=6)
        table.add_column("INTEL", width=6)
        
        if not self.missions:
            table.add_row("[dim]No active missions[/]", "", "", "", "")
        else:
            for m in self.missions[-5:]:
                table.add_row(
                    m["name"],
                    m["type"],
                    f"[green]{m['status']}[/]",
                    str(m.get("bots", 0)),
                    str(m.get("intel", 0)),
                )
        
        return Panel(table, title="[bold]ACTIVE MISSIONS[/]", border_style="cyan", box=box.ROUNDED)
    
    def render_log_panel(self):
        table = Table(box=None, show_header=False, show_edge=False)
        table.add_column(width=70)
        
        logs = list(self.logs)[-10:]
        if not logs:
            table.add_row("[dim]System initializing...[/]")
        else:
            for log in logs:
                table.add_row(log)
        
        return Panel(table, title="[bold]OPERATIONS LOG[/]", border_style="cyan", box=box.ROUNDED)
    
    def render_input_bar(self):
        return Panel(
            Text("  JEDI ▸ ", style="bold cyan") + Text("_", style="blink white"),
            title="[bold]COMMAND INPUT[/]", border_style="cyan", box=box.HEAVY
        )
    
    def render_full_dashboard(self):
        """Render the complete dashboard layout."""
        # Top section
        header = self.render_header()
        status = self.render_status_bar()
        
        # Middle section — 2 columns
        left_col = Layout()
        left_col.split_column(
            Layout(self.render_network_map(), ratio=3),
            Layout(self.render_missions_panel(), ratio=1),
        )
        
        right_col = Layout()
        right_col.split_column(
            Layout(self.render_threat_panel(), ratio=1),
            Layout(self.render_agents_panel(), ratio=2),
            Layout(self.render_alerts_panel(), ratio=2),
        )
        
        middle = Layout()
        middle.split_row(left_col, right_col)
        
        # Bottom section
        log_panel = self.render_log_panel()
        
        # Full layout
        full = Layout()
        full.split_column(
            Layout(header, size=7),
            Layout(status, size=3),
            Layout(middle, ratio=5),
            Layout(log_panel, ratio=1),
        )
        
        return full
    
    def handle_command(self, cmd):
        """Process user commands."""
        cmd = cmd.strip()
        if not cmd:
            return
        
        self.add_log(f"CMD: {cmd}")
        p = cmd.lower()
        
        if p in ["quit", "exit", "q"]:
            return "QUIT"
        
        if p == "clear":
            os.system("clear")
            return
        
        if p == "map":
            self.add_log("Network topology refreshed.")
            return
        
        if p == "status":
            return "STATUS"
        
        if p.startswith("threat") or p.startswith("assess"):
            self._cmd_threat(cmd)
            return
        
        if p.startswith("deploy"):
            self._cmd_deploy(cmd)
            return
        
        if p.startswith("scan"):
            self._cmd_scan(cmd)
            return
        
        if p.startswith("mission"):
            self._cmd_mission(cmd)
            return
        
        if p == "help":
            self._cmd_help()
            return
        
        # Route to LLM
        if self.engine:
            self.add_log(f"Cortex processing: {cmd[:40]}...")
            try:
                result = self.engine.think(
                    f"[JEDI CONTEXT] You are a cybersecurity operations AI. "
                    f"Current threat level: {self.threat_level}. "
                    f"Respond as a tactical cybersecurity specialist.\n\n{cmd}"
                )
                response = result["response"]
                lane = result["metadata"]["lane"]
                att = result["attestation"]["confidence"]
                
                self.add_log(f"[green]Response generated[/] — lane={lane} att={att:.2f}")
                
                # Print response
                print()
                for line in response.split("\n"):
                    if line.strip():
                        console.print(f"  [white]{line}[/]")
                print()
                
            except Exception as e:
                self.add_log(f"[red]Error: {e}[/]")
    
    def _cmd_threat(self, cmd):
        levels = {
            "none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4, "nation": 5
        }
        words = cmd.lower().split()
        for w in words:
            for key in levels:
                if key in w:
                    idx = levels[key]
                    self.threat_level = ["NONE","LOW","MEDIUM","HIGH","CRITICAL","NATION_STATE"][idx]
                    self.add_alert("THREAT", f"Threat level set to {self.threat_level}", "warn" if idx >= 3 else "info")
                    return
        
        # Assess from keywords
        score = 0
        p = cmd.lower()
        if any(w in p for w in ["apt", "nation", "state"]):
            score += 4
            self.add_alert("THREAT", "Nation-state indicators detected", "crit")
        if any(w in p for w in ["ransom", "malware"]):
            score += 3
            self.add_alert("THREAT", "Ransomware indicators detected", "error")
        if "phish" in p:
            score += 1
            self.add_alert("THREAT", "Phishing indicators detected", "warn")
        if any(w in p for w in ["exfil", "leak"]):
            score += 2
            self.add_alert("THREAT", "Data exfiltration indicators", "error")
        if "lateral" in p:
            score += 2
        
        if score >= 4:
            self.threat_level = "CRITICAL"
        elif score >= 3:
            self.threat_level = "HIGH"
        elif score >= 2:
            self.threat_level = "MEDIUM"
        elif score >= 1:
            self.threat_level = "LOW"
        else:
            self.threat_level = "MEDIUM"
            self.add_alert("THREAT", "General threat assessment requested", "info")
    
    def _cmd_deploy(self, cmd):
        parts = cmd.lower().split()
        bot_type = parts[1] if len(parts) > 1 else "scout"
        target = parts[3] if len(parts) > 3 else "10.0.0.1"
        
        bot_id = f"JEDI-{bot_type[:3].upper()}-{hashlib.md5(str(time.time()).encode()).hexdigest()[:6].upper()}"
        bot = {
            "id": bot_id,
            "type": bot_type.upper(),
            "state": "DEPLOYED",
            "mission": f"Op-{len(self.missions)+1:03d}",
            "uptime": "0s",
        }
        self.active_bots.append(bot)
        self.add_alert("DEPLOY", f"{bot_type.upper()} nanobot deployed to {target}", "info")
        self.add_log(f"Deployed {bot_id} → {target}")
    
    def _cmd_scan(self, cmd):
        parts = cmd.split()
        target = parts[1] if len(parts) > 1 else "10.0.0.0/24"
        self.add_alert("SCAN", f"Scanning {target}...", "info")
        self.add_log(f"Initiating scan of {target}")
        
        # Simulate findings
        time.sleep(0.1)
        findings = [
            ("10.0.0.10", "DC-01", "Domain Controller", "secure"),
            ("10.0.0.30", "WEB-01", "Nginx 1.24", "monitor"),
            ("10.0.0.40", "DB-01", "MySQL 8.0", "monitor"),
            ("10.0.0.50", "APP-01", "API Gateway", "monitor"),
            ("172.16.0.5", "HONEYPOT", "SSH Trap", "active"),
        ]
        print()
        console.print(f"  [bold cyan]SCAN RESULTS — {target}[/]")
        console.print(f"  {'─'*60}")
        for ip, name, svc, status in findings:
            s = {"secure": "[green]■ SECURE[/]", "monitor": "[yellow]■ MONITOR[/]", 
                 "threat": "[red]■ THREAT[/]", "active": "[cyan]◆ ACTIVE[/]"}
            console.print(f"  {s[status]}  {name:<12} {ip:<18} {svc}")
        console.print(f"  {'─'*60}")
        console.print(f"  [dim]5 hosts found. 0 threats. 3 requiring attention.[/]")
        print()
    
    def _cmd_mission(self, cmd):
        parts = cmd.lower().split()
        if "create" in parts:
            idx = parts.index("create") + 1
            mtype = parts[idx] if idx < len(parts) else "recon"
            target = parts[idx+1] if idx+1 < len(parts) else "10.0.0.0/24"
            name = f"Op-{len(self.missions)+1:03d}"
            self.missions.append({
                "name": name, "type": mtype.upper(), "status": "ACTIVE", "bots": 0, "intel": 0
            })
            self.add_alert("MISSION", f"Mission {name} created — {mtype} on {target}", "info")
            self.add_log(f"Mission {name}: {mtype} → {target}")
    
    def _cmd_help(self):
        print()
        console.print("  [bold cyan]JEDI OPERATIONS CENTER — COMMANDS[/]")
        console.print("  [dim]" + "─"*50 + "[/]")
        cmds = [
            ("help", "Show this help"),
            ("status", "System status report"),
            ("map", "Refresh network topology"),
            ("threat <info>", "Assess or set threat level"),
            ("deploy <type> to <ip>", "Deploy a nanobot"),
            ("scan <target>", "Scan network segment"),
            ("mission create <type> <target>", "Create a mission"),
            ("quit", "Shutdown JEDI"),
            ("", ""),
            ("", "Type anything else for LLM-powered analysis."),
        ]
        for cmd, desc in cmds:
            if cmd:
                console.print(f"  [bold white]{cmd:<35}[/] [dim]{desc}[/]")
            else:
                console.print()
        console.print()
    
    def run(self):
        """Main interactive loop."""
        os.system("clear")
        console.print(self.render_full_dashboard())
        console.print()
        console.print("  [dim]Type 'help' for commands. Type 'quit' to exit.[/]")
        console.print()
        
        while True:
            try:
                cmd = console.input("  [bold cyan]JEDI ▸ [/]")
            except (EOFError, KeyboardInterrupt):
                console.print("\n  [dim]Shutdown. Ledger sealed.[/]")
                break
            
            result = self.handle_command(cmd)
            if result == "QUIT":
                console.print("\n  [dim]Shutdown. All nanobots self-destructed. Ledger verified.[/]\n")
                break
            
            # Refresh dashboard
            console.print()
            console.print(self.render_full_dashboard())
            console.print()
            console.print("  [dim]Type 'help' for commands. Type 'quit' to exit.[/]")
            console.print()


if __name__ == "__main__":
    app = JEDITerminal()
    app.run()
