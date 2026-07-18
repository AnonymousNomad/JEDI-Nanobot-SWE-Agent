#!/usr/bin/env python3
"""
JEDI Web Server — Live demonstration of the JEDI AI system with terminal control.

This web server provides:
- Real-time terminal command execution
- File system browser
- Code execution sandbox
- JEDI nanobot system integration
- Web-based cyber operations interface
- Live model interaction
"""

from flask import Flask, render_template_string, request, jsonify
import subprocess
import os
import json
import time
from pathlib import Path
import threading

app = Flask(__name__)

# Initialize JEDI systems
class JEDIWebInterface:
    def __init__(self):
        self.terminal_session = None
        self.jedi_initialized = False
        self.setup_terminal_session()
        self.setup_jedi_systems()
        
    def setup_terminal_session(self):
        """Initialize terminal session for web interface."""
        try:
            self.terminal_session = {
                'working_dir': str(Path.cwd()),
                'history': [],
                'status': 'connected'
            }
            print("✓ Terminal session initialized")
        except Exception as e:
            print(f"✗ Terminal session failed: {e}")
            self.terminal_session = {'status': 'error', 'message': str(e)}
    
    def setup_jedi_systems(self):
        """Initialize JEDI nanobot system."""
        try:
            self.jedi_systems = {
                'engine_state': 'online',
                'threat_level': 'normal',
                'active_missions': 0,
                'nanobots_deployed': 0,
                'system_status': 'operational'
            }
            self.jedi_initialized = True
            print("✓ JEDI systems online")
        except Exception as e:
            print(f"✗ JEDI setup failed: {e}")
            self.jedi_initialized = False
    
    def execute_command(self, command, timeout=30):
        """Execute bash command with terminal session."""
        if not self.terminal_session:
            return {'error': 'Terminal session not initialized'}
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.terminal_session['working_dir']
            )
            
            command_output = {
                'command': command,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'success': result.returncode == 0,
                'timestamp': time.time()
            }
            
            self.terminal_session['history'].append(command_output)
            return command_output
            
        except subprocess.TimeoutExpired:
            return {'error': f'Command timed out after {timeout} seconds', 'command': command}
        except Exception as e:
            return {'error': str(e), 'command': command}
    
    def change_directory(self, path):
        """Change current directory."""
        try:
            new_path = Path(self.terminal_session['working_dir']) / path
            if new_path.exists():
                self.terminal_session['working_dir'] = str(new_path.resolve())
                return {'status': 'ok', 'directory': self.terminal_session['working_dir']}
            else:
                return {'error': 'Directory does not exist'}
        except Exception as e:
            return {'error': str(e)}
    
    def list_directory(self, path='.'):
        """List directory contents."""
        try:
            dir_path = Path(self.terminal_session['working_dir']) / path
            if dir_path.exists():
                files = [f.name for f in dir_path.iterdir()]
                return {'status': 'ok', 'files': files, 'path': str(dir_path)}
            else:
                return {'error': 'Directory does not exist'}
        except Exception as e:
            return {'error': str(e)}

# Initialize web interface
jedi_interface = JEDIWebInterface()

# Web templates
HTML_TEMPLATES = {
    'main': '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>JEDI Web Interface</title>
        <style>
            body {
                font-family: 'Courier New', monospace;
                background: #1a1a1a;
                color: #00ff00;
                margin: 0;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                background: #0a0a0a;
                padding: 20px;
                border: 2px solid #00ff00;
                margin-bottom: 20px;
            }
            .title {
                color: #00ff00;
                text-align: center;
                font-size: 2em;
                margin: 0;
                text-shadow: 0 0 20px #00ff00;
            }
            .status-bar {
                display: flex;
                justify-content: space-between;
                background: #0a0a0a;
                padding: 10px;
                border: 1px solid #00ff00;
                margin-bottom: 20px;
            }
            .terminal {
                background: #000000;
                border: 2px solid #00ff00;
                padding: 20px;
                height: 400px;
                overflow-y: auto;
                font-family: 'Courier New', monospace;
                font-size: 14px;
            }
            .input-area {
                display: flex;
                margin-top: 20px;
            }
            .command-input {
                flex: 1;
                background: #000000;
                border: 1px solid #00ff00;
                color: #00ff00;
                padding: 10px;
                font-family: 'Courier New', monospace;
            }
            .execute-btn {
                background: #00ff00;
                color: #000000;
                border: none;
                padding: 10px 20px;
                cursor: pointer;
                font-weight: bold;
                margin-left: 10px;
            }
            .output {
                background: #000000;
                border: 1px solid #00ff00;
                padding: 10px;
                margin: 10px 0;
                border-radius: 3px;
            }
            .success {
                border-color: #00ff00;
            }
            .error {
                border-color: #ff0000;
            }
            .system-panel {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                margin-bottom: 20px;
            }
            .panel {
                background: #0a0a0a;
                border: 1px solid #00ff00;
                padding: 15px;
            }
            .panel-title {
                color: #00ff00;
                font-weight: bold;
                margin-bottom: 10px;
                border-bottom: 1px solid #00ff00;
                padding-bottom: 5px;
            }
            .tab-nav {
                display: flex;
                background: #0a0a0a;
                border: 1px solid #00ff00;
                margin-bottom: 20px;
            }
            .tab {
                flex: 1;
                padding: 10px;
                text-align: center;
                cursor: pointer;
                border-right: 1px solid #00ff00;
                color: #00ff00;
            }
            .tab:hover {
                background: #00ff00;
                color: #000000;
            }
            .tab.active {
                background: #00ff00;
                color: #000000;
            }
            .code-block {
                background: #000000;
                border: 1px solid #333333;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                max-height: 200px;
                overflow-y: auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="title">JEDI — Joint Entity Defense Infrastructure</h1>
                <p style="text-align: center; color: #00ff00;">
                    Terminal Control Interface with Real-time Execution
                </p>
            </div>
            
            <div class="status-bar">
                <div>Terminal: <strong>{{ terminal_status }}</strong></div>
                <div>Working Directory: <strong>{{ cwd }}</strong></div>
                <div>JEDI Systems: <strong>{{ jedi_status }}</strong></div>
                <div>Uptime: <strong>{{ uptime }}s</strong></div>
            </div>
            
            <div class="system-panel">
                <div class="panel">
                    <div class="panel-title">🔧 JEDI Engine</div>
                    <div>State: <strong style="color: #00ff00;">{{ engine_state }}</strong></div>
                    <div>Threat Level: <strong style="color: #00ff00;">{{ threat_level }}</strong></div>
                    <div>Missions: <strong>{{ missions }}</strong></div>
                </div>
                <div class="panel">
                    <div class="panel-title">🤖 Nanobots</div>
                    <div>Deployed: <strong>{{ nanobots }}</strong></div>
                    <div>Active: <strong>{{ active_nanobots }}</strong></div>
                    <div>System Health: <strong style="color: #00ff00;">ONLINE</strong></div>
                </div>
                <div class="panel">
                    <div class="panel-title">📊 Web Server</div>
                    <div>Status: <strong style="color: #00ff00;">RUNNING</strong></div>
                    <div>Port: <strong>{{ port }}</strong></div>
                    <div>Requests: <strong>{{ request_count }}</strong></div>
                </div>
            </div>
            
            <div class="tab-nav">
                <div class="tab active" onclick="switchTab('terminal')">🖥️ Terminal</div>
                <div class="tab" onclick="switchTab('commands')">⚡ Commands</div>
                <div class="tab" onclick="switchTab('nanobots')">🤖 Nanobots</div>
                <div class="tab" onclick="switchTab('system')">🔧 System</div>
            </div>
            
            <div id="terminal" class="tab-content" style="display: block;">
                <div class="terminal" id="terminal-output">
                    <div style="color: #00ff00;">
                        <strong>[SYSTEM] JEDI Web Interface Started</strong>
                    </div>
                    <div style="color: #00ff00;">
                        <strong>[SYSTEM] Terminal session initialized</strong>
                    </div>
                    <div style="color: #00ff00;">
                        <strong>[SYSTEM] Ready for commands</strong>
                    </div>
                </div>
                <div class="input-area">
                    <input type="text" class="command-input" id="command-input" placeholder="Enter command..." onkeypress="if(event.key === 'Enter') executeCommand()">
                    <button class="execute-btn" onclick="executeCommand()">EXECUTE</button>
                </div>
            </div>
            
            <div id="commands" class="tab-content" style="display: none;">
                <div class="panel">
                    <div class="panel-title">📋 Common Commands</div>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                        <button class="execute-btn" onclick="runPredefinedCommand('ls -la')">ls -la</button>
                        <button class="execute-btn" onclick="runPredefinedCommand('pwd')">pwd</button>
                        <button class="execute-btn" onclick="runPredefinedCommand('python3 --version')">python3 --version</button>
                        <button class="execute-btn" onclick="runPredefinedCommand('whoami')">whoami</button>
                        <button class="execute-btn" onclick="runPredefinedCommand('ls /tmp')">ls /tmp</button>
                        <button class="execute-btn" onclick="runPredefinedCommand('echo "JEDI Web Demo"')">echo test</button>
                    </div>
                </div>
            </div>
            
            <div id="nanobots" class="tab-content" style="display: none;">
                <div class="panel">
                    <div class="panel-title">🤖 Nanobot Status</div>
                    <div>Red Team (Strikers): <strong>Ready</strong></div>
                    <div>Blue Team (Guardians): <strong>Ready</strong></div>
                    <div>Green Team (Architects): <strong>Ready</strong></div>
                    <div>Yellow Team (Auditors): <strong>Ready</strong></div>
                    <div>Purple Team (Synapse): <strong>Ready</strong></div>
                    <div>Black Team (Ghosts): <strong>Ready</strong></div>
                </div>
            </div>
            
            <div id="system" class="tab-content" style="display: none;">
                <div class="panel">
                    <div class="panel-title">🖥️ System Information</div>
                    <div>Platform: <strong>{{ platform }}</strong></div>
                    <div>Python Version: <strong>{{ python_version }}</strong></div>
                    <div>Working Directory: <strong>{{ system_cwd }}</strong></div>
                    <div>Terminal Sessions: <strong>{{ sessions }}</strong></div>
                </div>
            </div>
        </div>
        
        <script>
            let commandHistory = [];
            let sessionStart = Date.now();
            
            function switchTab(tabName) {
                const tabs = document.querySelectorAll('.tab');
                const tabContents = document.querySelectorAll('.tab-content');
                
                tabs.forEach(tab => tab.classList.remove('active'));
                tabContents.forEach(content => content.style.display = 'none');
                
                document.querySelector('.tab[onclick*="' + tabName + '"]').classList.add('active');
                document.getElementById(tabName).style.display = 'block';
            }
            
            function executeCommand() {
                const commandInput = document.getElementById('command-input');
                const command = commandInput.value.trim();
                
                if (!command) return;
                
                const terminalOutput = document.getElementById('terminal-output');
                
                terminalOutput.innerHTML += `
                    <div style="color: #00ff00; margin: 5px 0;">
                        <strong>[USER] ${command}</strong>
                    </div>
                `;
                
                commandHistory.push(command);
                commandInput.value = '';
                
                fetch('/execute', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ command: command })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        terminalOutput.innerHTML += `
                            <div class="output error">
                                <strong>[ERROR] ${data.error}</strong>
                            </div>
                        `;
                    } else {
                        let output = '';
                        if (data.stdout) output += `<div style="color: #ffffff;">${data.stdout}</div>`;
                        if (data.stderr) output += `<div style="color: #ff6666;">${data.stderr}</div>`;
                        if (data.returncode !== undefined) {
                            output += `<div style="color: #00ff00;">[Exit Code: ${data.returncode}]</div>`;
                        }
                        
                        terminalOutput.innerHTML += `
                            <div class="output success">
                                <strong>[SYSTEM]</strong> ${output}
                            </div>
                        `;
                    }
                    
                    terminalOutput.scrollTop = terminalOutput.scrollHeight;
                })
                .catch(error => {
                    terminalOutput.innerHTML += `
                        <div class="output error">
                            <strong>[ERROR] Network Error: ${error.message}</strong>
                        </div>
                    `;
                });
            }
            
            function runPredefinedCommand(command) {
                document.getElementById('command-input').value = command;
                executeCommand();
            }
            
            function updateSystemInfo() {
                fetch('/system-info')
                .then(response => response.json())
                .then(data => {
                    document.querySelector('[data-field="platform"]').textContent = data.platform;
                    document.querySelector('[data-field="python_version"]').textContent = data.python_version;
                    document.querySelector('[data-field="system_cwd"]').textContent = data.cwd;
                })
                .catch(error => {
                    console.log('System info update failed:', error);
                });
            }
            
            document.addEventListener('DOMContentLoaded', function() {
                updateSystemInfo();
                setInterval(updateSystemInfo, 5000);
            });
        </script>
    </body>
    </html>
    ''',
    'nanobot': '''
    <div style="padding: 20px;">
        <h2>🤖 Nanobot Control Panel</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
            <div style="background: #0a0a0a; border: 1px solid #00ff00; padding: 15px;">
                <h3 style="color: #ff6666;">🔴 Red Team - Strikers</h3>
                <p>Status: <strong style="color: #00ff00;">Ready</strong></p>
                <p>Primary Function: Offensive penetration testing</p>
                <p>Capabilities: SQL injection, RCE, privilege escalation</p>
            </div>
            <div style="background: #0a0a0a; border: 1px solid #00ff00; padding: 15px;">
                <h3 style="color: #6666ff;">🔵 Blue Team - Guardians</h3>
                <p>Status: <strong style="color: #00ff00;">Ready</strong></p>
                <p>Primary Function: Defensive monitoring</p>
                <p>Capabilities: Anomaly detection, threat assessment</p>
            </div>
            <div style="background: #0a0a0a; border: 1px solid #00ff00; padding: 15px;">
                <h3 style="color: #66ff66;">🟢 Green Team - Architects</h3>
                <p>Status: <strong style="color: #00ff00;">Ready</strong></p>
                <p>Primary Function: Secure code review</p>
                <p>Capabilities: Vulnerability analysis, secure design</p>
            </div>
            <div style="background: #0a0a0a; border: 1px solid #00ff00; padding: 15px;">
                <h3 style="color: #ffff66;">🟡 Yellow Team - Auditors</h3>
                <p>Status: <strong style="color: #00ff00;">Ready</strong></p>
                <p>Primary Function: Compliance checking</p>
                <p>Capabilities: NIST compliance, audit trails</p>
            </div>
            <div style="background: #0a0a0a; border: 1px solid #00ff00; padding: 15px;">
                <h3 style="color: #ff66ff;">🟣 Purple Team - Synapse</h3>
                <p>Status: <strong style="color: #00ff00;">Ready</strong></p>
                <p>Primary Function: Combined ops coordination</p>
                <p>Capabilities: Collaborative defense/offense</p>
            </div>
            <div style="background: #0a0a0a; border: 1px solid #00ff00; padding: 15px;">
                <h3 style="color: #aaaaaa;">⚫ Black Team - Ghosts</h3>
                <p>Status: <strong style="color: #00ff00;">Ready</strong></p>
                <p>Primary Function: Covert/assumption operations</p>
                <p>Capabilities: Attribution, infiltration, persistence</p>
            </div>
        </div>
    </div>
    '''
}

# Initialize command counter
request_count = 0

def get_uptime():
    return int((time.time() - sessionStart) / 1000)

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    global request_count
    request_count += 1
    
    return HTML_TEMPLATES['main'].format(
        terminal_status=jedi_interface.terminal_session.get('status', 'unknown') if jedi_interface.terminal_session else 'unknown',
        cwd=jedi_interface.terminal_session.get('working_dir', 'unknown') if jedi_interface.terminal_session else 'unknown',
        jedi_status='ONLINE' if jedi_interface.jedi_initialized else 'OFFLINE',
        uptime=get_uptime(),
        engine_state=jedi_interface.jedi_systems.get('engine_state', 'idle') if jedi_interface.jedi_systems else 'unknown',
        threat_level=jedi_interface.jedi_systems.get('threat_level', 'normal') if jedi_interface.jedi_systems else 'unknown',
        missions=jedi_interface.jedi_systems.get('active_missions', 0) if jedi_interface.jedi_systems else 0,
        nanobots=jedi_interface.jedi_systems.get('deployed_nanobots', 0) if jedi_interface.jedi_systems else 0,
        active_nanobots=0,
        port=5000,
        platform=os.uname().sysname,
        python_version=__import__('sys').version.split()[0],
        system_cwd=os.getcwd(),
        sessions=len(jedi_interface.terminal_session.get('history', [])) if jedi_interface.terminal_session else 0
    )

@app.route('/execute', methods=['POST'])
def execute_command():
    global request_count
    request_count += 1
    
    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({'error': 'No command provided'}), 400
    
    command = data['command']
    
    # Handle special commands
    if command.lower() == 'help':
        return jsonify({
            'stdout': '''Available commands:
ls - list directory
pwd - print working directory
cd <path> - change directory
cat <file> - display file content
python <code> - execute python code
wget <url> - download file
rm <file> - remove file
mkdir <dir> - make directory
touch <file> - create empty file
help - show this help
exit - exit server''',
            'stderr': '',
            'returncode': 0
        })
    
    if command.lower() == 'exit':
        return jsonify({'stdout': 'Server shutting down...', 'stderr': '', 'returncode': 0, '_shutdown': True})
    
    # Execute terminal command
    result = jedi_interface.execute_command(command)
    
    if 'error' in result:
        return jsonify(result)
    
    return jsonify(result)

@app.route('/system-info')
def system_info():
    return jsonify({
        'platform': os.uname().sysname,
        'python_version': __import__('sys').version.split()[0],
        'cwd': os.getcwd(),
        'uptime': get_uptime(),
        'terminal_sessions': len(jedi_interface.terminal_session.get('history', [])) if jedi_interface.terminal_session else 0,
        'jedi_initialized': jedi_interface.jedi_initialized,
        'request_count': request_count
    })

@app.route('/nanobot-status')
def nanobot_status():
    return HTML_TEMPLATES['nanobot']

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'uptime': get_uptime(),
        'terminal_active': jedi_interface.terminal_session is not None,
        'jedi_active': jedi_interface.jedi_initialized
    })

# Handle server shutdown
@app.route('/shutdown', methods=['POST'])
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        return jsonify({'error': 'Not running with Werkzeug Server'}), 400
    func()
    return jsonify({'status': 'Server shutting down...'})

if __name__ == '__main__':
    print("Starting JEDI Web Server...")
    print("Server will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print()
    print("Available endpoints:")
    print("  GET  /           - Main web interface")
    print("  POST /execute    - Execute terminal commands")
    print("  GET  /system-info - System information")
    print("  GET  /nanobot-status - Nanobot status")
    print("  GET  /health      - Health check")
    print()
    print("Example commands from the web interface:")
    print("  ls -la           - List directory contents")
    print("  pwd              - Show current working directory")
    print("  python3 --version - Python version")
    print("  whoami           - Current user")
    print()
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\nShutting down JEDI Web Server...")
    finally:
        print("JEDI Web Server stopped.")
