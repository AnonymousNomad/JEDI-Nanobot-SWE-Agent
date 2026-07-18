#!/usr/bin/env python3
"""
JEDI Web Server - Demonstration of Terminal Control Capabilities

This simple web server demonstrates what the JEDI model can do:
- Real-time terminal command execution
- File system management
- Code execution
- Live web interface
- Full terminal integration

The server can be accessed at: http://localhost:5000
"""

from flask import Flask, render_template_string, request, jsonify
import subprocess
import os
import time
from pathlib import Path
import threading

app = Flask(__name__)

# Global terminal controller instance
class TerminalController:
    def __init__(self):
        self.working_dir = Path.cwd()
        self.command_history = []
        
    def execute_bash(self, command, timeout=30):
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.working_dir),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            output = {
                'command': command,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'success': result.returncode == 0
            }
            
            self.command_history.append(output)
            return output
        except Exception as e:
            return {'error': str(e), 'command': command}
    
    def get_files(self, path='.'):
        try:
            dir_path = Path(self.working_dir) / path
            if dir_path.exists():
                return [f.name for f in dir_path.iterdir()]
            return []
        except:
            return []
    
    def get_working_dir(self):
        return str(self.working_dir)

# Initialize controller
terminal = TerminalController()

# Simple web interface HTML
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>JEDI Terminal Control Demo</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #0a0a0a;
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
            text-align: center;
        }
        .title {
            color: #00ff00;
            font-size: 2.5em;
            margin: 0;
            text-shadow: 0 0 20px #00ff00;
        }
        .status-bar {
            display: flex;
            justify-content: space-around;
            background: #0a0a0a;
            padding: 15px;
            border: 1px solid #00ff00;
            margin-bottom: 20px;
            border-radius: 5px;
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
            padding: 10px 25px;
            cursor: pointer;
            font-weight: bold;
            margin-left: 10px;
            font-family: 'Courier New', monospace;
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
            border-color: #ff6666;
        }
        .command-prompt {
            color: #00ff00;
            font-weight: bold;
        }
        .info-box {
            background: #0a0a0a;
            border: 1px solid #00ff00;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .feature-card {
            background: #0a0a0a;
            border: 1px solid #00ff00;
            padding: 20px;
            border-radius: 5px;
        }
        .feature-icon {
            font-size: 2em;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">🦾 JEDI Terminal Control</h1>
            <p>Real-time bash execution with full terminal integration</p>
        </div>
        
        <div class="status-bar">
            <div><strong>Terminal:</strong> <span style="color: #00ff00;">Active</span></div>
            <div><strong>Working Dir:</strong> <span style="color: #00ff00;">{{ cwd }}</span></div>
            <div><strong>Commands Executed:</strong> <span style="color: #00ff00;">{{ command_count }}</span></div>
            <div><strong>Server Status:</strong> <span style="color: #00ff00;">Running</span></div>
        </div>
        
        <div class="features">
            <div class="feature-card">
                <div class="feature-icon">🖥️</div>
                <h3>Real Bash Execution</h3>
                <p>Execute any bash command in real-time with full output capture</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📁</div>
                <h3>File System Control</h3>
                <p>Create, read, write, and delete files and directories</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🐍</div>
                <h3>Code Execution</h3>
                <p>Run Python, JavaScript, and other scripts directly in the browser</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🌐</div>
                <h3>Web Integration</h3>
                <p>Fully integrated web interface with live command execution</p>
            </div>
        </div>
        
        <div class="info-box">
            <h3>🚀 Demo Instructions</h3>
            <p>Type any bash command below (e.g., <code>ls -la</code>, <code>pwd</code>, <code>python3 -c "print('hello')"</code>) and watch it execute in real-time!</p>
            <p>The JEDI model demonstrates full terminal control capabilities here. Try some commands to see what it can do.</p>
        </div>
        
        <h2>🖥️ Interactive Terminal</h2>
        <div id="terminal" class="terminal">
            <div style="color: #00ff00;">
                <span class="command-prompt">JEDI SYSTEM:</span> Terminal Control Interface initialized successfully
            </div>
            <div style="color: #00ff00;">
                <span class="command-prompt">JEDI SYSTEM:</span> Ready for command execution
            </div>
            <div style="color: #00ff00;">
                <span class="command-prompt">JEDI SYSTEM:</span> Use the input box below to send commands
            </div>
        </div>
        
        <div class="input-area">
            <input type="text" class="command-input" id="command-input" placeholder="Enter bash command... (e.g., ls -la, pwd, whoami)" onkeypress="handleKeyPress(event)">
            <button class="execute-btn" onclick="executeCommand()">EXECUTE</button>
        </div>
        
        <div class="info-box">
            <h3>📊 Quick Test Commands</h3>
            <p>Try these sample commands to test JEDI capabilities:</p>
            <ul>
                <li><code onclick="quickCommand('ls -la')">ls -la</code> - List directory contents</li>
                <li><code onclick="quickCommand('pwd')">pwd</code> - Show current directory</li>
                <li><code onclick="quickCommand('python3 -c \"print(\\\"Hello from JEDI\\\")\"')">python3 -c "print('hello')"</code> - Execute Python</li>
                <li><code onclick="quickCommand('echo \"Terminal test successful!\"')">echo "Terminal test successful!"</code> - Simple command test</li>
            </ul>
        </div>
    </div>
    
    <script>
        let commandCount = 0;
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                executeCommand();
            }
        }
        
        function executeCommand() {
            const commandInput = document.getElementById('command-input');
            const command = commandInput.value.trim();
            
            if (!command) return;
            
            const terminal = document.getElementById('terminal');
            
            // Add user command to terminal
            terminal.innerHTML += `
                <div style="color: #00ff00; margin: 8px 0;">
                    <span class="command-prompt">[USER] ${command}</span>
                </div>
            `;
            
            commandInput.value = '';
            
            // Send command to server
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
                    terminal.innerHTML += `
                        <div class="output error">
                            <span class="command-prompt">[ERROR] ${data.error}</span>
                        </div>
                    `;
                } else {
                    let output = '';
                    if (data.stdout) {
                        output += `<div style="color: #ffffff;">${data.stdout}</div>`;
                    }
                    if (data.stderr && data.stderr.trim()) {
                        output += `<div style="color: #ff6666;">${data.stderr}</div>`;
                    }
                    if (data.returncode !== undefined) {
                        const statusColor = data.success ? '#00ff00' : '#ff6666';
                        output += `<div style="color: ${statusColor}; font-weight: bold;">[Exit: ${data.returncode}]</div>`;
                    }
                    
                    terminal.innerHTML += `
                        <div class="output success">
                            <span class="command-prompt">[SYSTEM]</span> ${output}
                        </div>
                    `;
                    commandCount++;
                }
                
                terminal.scrollTop = terminal.scrollHeight;
            })
            .catch(error => {
                terminal.innerHTML += `
                    <div class="output error">
                        <span class="command-prompt">[ERROR] Network Error: ${error.message}</span>
                    </div>
                `;
            });
        }
        
        function quickCommand(command) {
            document.getElementById('command-input').value = command;
            executeCommand();
        }
        
        // Update status periodically
        function updateStatus() {
            fetch('/system-info')
            .then(response => response.json())
            .then(data => {
                // Update UI with system info if needed
                console.log('System info updated:', data);
            })
            .catch(error => {
                console.log('Status update failed:', error);
            });
        }
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            // Add welcome message
            const terminal = document.getElementById('terminal');
            terminal.innerHTML += `
                <div class="output success">
                    <span class="command-prompt">[SYSTEM]</span> 
                    Welcome to JEDI Terminal Control! The model is ready to execute commands. 
                    Try some commands above to see real bash execution in action.
                </div>
            `;
            
            // Start periodic status updates
            setInterval(updateStatus, 5000);
        });
    </script>
</body>
</html>
''', locals={'cwd': terminal.get_working_dir(), 'command_count': 0}

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, 
        cwd=terminal.get_working_dir(), 
        command_count=len(terminal.command_history))

@app.route('/execute', methods=['POST'])
def execute():
    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({'error': 'No command provided'}), 400
    
    result = terminal.execute_bash(data['command'])
    return jsonify(result)

@app.route('/system-info')
def system_info():
    return jsonify({
        'cwd': terminal.get_working_dir(),
        'command_count': len(terminal.command_history),
        'status': 'running'
    })

if __name__ == '__main__':
    print("🚀 JEDI Terminal Control Web Server Starting...")
    print("=" * 60)
    print("Server will be available at: http://localhost:5000")
    print("=" * 60)
    print("\nFeatures demonstrated:")
    print("• Real bash command execution")
    print("• File system operations")
    print("• Code execution")
    print("• Live terminal interface")
    print("• JEDI integration")
    print("\nTest the model by visiting http://localhost:5000")
    print("in your web browser and trying some commands!")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
