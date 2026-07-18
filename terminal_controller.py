#!/usr/bin/env python3
"""
JEDI Terminal Control Module — Real bash terminal integration.

This module provides actual terminal control capabilities, enabling the model to:
- Execute real bash commands
- Create/manipulate files and directories
- Download/upload files from the internet
- Run arbitrary code snippets
- Maintain persistent terminal session
- Extract and execute proposed commands
- File system operations for development workflows

This is the foundation for true terminal mastery, matching what users expect from terminal-based AI assistants.
"""

import os
import sys
import subprocess
import tempfile
import shutil
import threading
import time
import json
import urllib.request
import urllib.error
import signal
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

@dataclass
class TerminalCommandResult:
    """Result of a terminal command execution."""
    command: str
    stdout: str
    stderr: str
    returncode: int
    execution_time: float
    success: bool
    error_message: Optional[str] = None

class TerminalController:
    """
    Real terminal controller with full bash access.
    
    Provides capabilities for:
    - Command execution with output capture
    - File system operations
    - Directory navigation
    - File downloads and uploads
    - Code execution in various languages
    - Process management
    """
    
    def __init__(self, working_directory: Optional[str] = None, timeout: int = 30):
        self.working_directory = Path(working_directory or os.getcwd()).resolve()
        self.timeout = timeout
        self.command_history: List[TerminalCommandResult] = []
        self.active_processes: Dict[int, subprocess.Popen] = {}
        self.session_active = True
        
        # Create a persistent shell context for more advanced operations
        self.shell_process = None
        self._init_terminal_session()
        
    def _init_terminal_session(self):
        """Initialize a persistent shell session."""
        try:
            # Create a shell that maintains environment across commands
            self.shell_process = subprocess.Popen(
                ["bash", "--noprofile", "--norc", "-i"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.working_directory),
                preexec_fn=os.setsid
            )
            # Give the shell time to initialize
            time.sleep(0.5)
        except Exception as e:
            print(f"[Terminal] Shell session initialization failed: {e}")
            self.shell_process = None
    
    def execute_bash_command(self, command: str, capture_output: bool = True) -> TerminalCommandResult:
        """
        Execute a real bash command.
        
        Args:
            command: The bash command to execute
            capture_output: Whether to capture stdout/stderr
            
        Returns:
            TerminalCommandResult with execution details
        """
        start_time = time.time()
        
        try:
            if capture_output:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=str(self.working_directory),
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                stdout, stderr = result.stdout, result.stderr
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=str(self.working_directory),
                    timeout=self.timeout
                )
                stdout, stderr = "", ""
                
            execution_time = time.time() - start_time
            success = result.returncode == 0
            
            terminal_result = TerminalCommandResult(
                command=command,
                stdout=stdout,
                stderr=stderr,
                returncode=result.returncode,
                execution_time=execution_time,
                success=success
            )
            
            self.command_history.append(terminal_result)
            return terminal_result
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            terminal_result = TerminalCommandResult(
                command=command,
                stdout="",
                stderr=f"Command timed out after {self.timeout} seconds",
                returncode=-1,
                execution_time=execution_time,
                success=False,
                error_message=f"Command timed out after {self.timeout} seconds"
            )
            self.command_history.append(terminal_result)
            return terminal_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            terminal_result = TerminalCommandResult(
                command=command,
                stdout="",
                stderr=f"Execution error: {e}",
                returncode=-1,
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
            self.command_history.append(terminal_result)
            return terminal_result
    
    def file_exists(self, path: str) -> bool:
        """Check if a file or directory exists."""
        return (self.working_directory / path).exists()
    
    def read_file(self, path: str) -> str:
        """Read contents of a file."""
        file_path = self.working_directory / path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file {path}: {e}"
    
    def write_file(self, path: str, content: str) -> bool:
        """Write content to a file."""
        file_path = self.working_directory / path
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"[Terminal] Error writing file {path}: {e}")
            return False
    
    def create_directory(self, path: str) -> bool:
        """Create a directory."""
        dir_path = self.working_directory / path
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"[Terminal] Error creating directory {path}: {e}")
            return False
    
    def list_directory(self, path: str = ".") -> List[str]:
        """List contents of a directory."""
        dir_path = self.working_directory / path
        try:
            return [str(item.name) for item in dir_path.iterdir()]
        except Exception as e:
            return [f"Error listing directory {path}: {e}"]
    
    def download_file(self, url: str, destination: str) -> bool:
        """
        Download a file from the internet.
        
        Args:
            url: URL to download from
            destination: Local path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            dest_path = self.working_directory / destination
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            urllib.request.urlretrieve(url, str(dest_path))
            return True
        except urllib.error.HTTPError as e:
            print(f"[Terminal] HTTP error downloading {url}: {e.code} {e.reason}")
            return False
        except urllib.error.URLError as e:
            print(f"[Terminal] URL error downloading {url}: {e.reason}")
            return False
        except Exception as e:
            print(f"[Terminal] Error downloading {url}: {e}")
            return False
    
    def run_python_code(self, code: str) -> str:
        """Execute Python code."""
        result = self.execute_bash_command(f"python3 -c \"{code}\"")
        return result.stdout.strip()
    
    def run_javascript_code(self, code: str) -> str:
        """Execute JavaScript code using Node if available."""
        result = self.execute_bash_command(f"node -e \"{code}\"")
        return result.stdout.strip()
    
    def run_bash_script(self, script_path: str) -> bool:
        """Execute a bash script from a file."""
        if not self.file_exists(script_path):
            print(f"[Terminal] Script {script_path} does not exist")
            return False
        
        # Read the script content
        content = self.read_file(script_path)
        
        # Execute the script with proper line handling
        safe_script = content.replace('"', '\\"').replace('`', '\\`')
        result = self.execute_bash_command(f"bash -c \"{safe_script}\"")
        
        if result.success:
            return True
        else:
            print(f"[Terminal] Script execution failed: {result.stderr}")
            return False
    
    def get_working_directory(self) -> str:
        """Get the current working directory."""
        return str(self.working_directory)
    
    def change_directory(self, path: str) -> bool:
        """Change the working directory."""
        new_dir = (self.working_directory / path).resolve()
        if new_dir.exists() and new_dir.is_dir():
            self.working_directory = new_dir
            # Update shell session if active
            if self.shell_process:
                self.shell_process.terminate()
                time.sleep(0.1)
                self._init_terminal_session()
            return True
        return False
    
    def get_command_history(self, limit: int = 10) -> List[TerminalCommandResult]:
        """Get recent command history."""
        return self.command_history[-limit:]
    
    def get_system_info(self) -> str:
        """Get system information."""
        result = self.execute_bash_command("uname -a && df -h . && free -h")
        return result.stdout
    
    def cleanup(self):
        """Clean up terminal session."""
        self.session_active = False
        if self.shell_process:
            try:
                os.killpg(os.getpgid(self.shell_process.pid), signal.SIGTERM)
            except:
                pass
            self.shell_process = None

# Global terminal controller instance
_terminal_controller = None

def get_terminal_controller() -> TerminalController:
    """Get or create the global terminal controller."""
    global _terminal_controller
    if _terminal_controller is None:
        _terminal_controller = TerminalController()
    return _terminal_controller

def terminal_execute(command: str) -> str:
    """
    Convenience function for executing terminal commands.
    
    Args:
        command: The command to execute
        
    Returns:
        String representation of the command result
    """
    controller = get_terminal_controller()
    result = controller.execute_bash_command(command)
    
    output_parts = []
    if result.stdout:
        output_parts.append(result.stdout)
    if result.stderr and result.returncode != 0:
        output_parts.append(f"STDERR: {result.stderr}")
    
    status = "✓ SUCCESS" if result.success else "✗ FAILED"
    output_parts.append(f"\n[Status: {status}] Command: {command}")
    
    return "\n".join(output_parts)

def terminal_read_file(path: str) -> str:
    """Convenience function for reading files."""
    controller = get_terminal_controller()
    return controller.read_file(path)

def terminal_write_file(path: str, content: str) -> bool:
    """Convenience function for writing files."""
    controller = get_terminal_controller()
    return controller.write_file(path, content)

def terminal_list_files(path: str = ".") -> List[str]:
    """Convenience function for listing directory contents."""
    controller = get_terminal_controller()
    return controller.list_directory(path)

def terminal_download(url: str, dest: str) -> bool:
    """Convenience function for downloading files."""
    controller = get_terminal_controller()
    return controller.download_file(url, dest)

if __name__ == "__main__":
    # Demo terminal control capabilities
    controller = TerminalController()
    
    print("=== JEDI Terminal Control Demo ===")
    
    # Test directory operations
    print("\n1. Directory operations:")
    print(f"   Current dir: {controller.get_working_directory()}")
    controller.create_directory("demo_dir/subdir")
    print(f"   Created demo_dir/subdir")
    
    # Test file operations
    print("\n2. File operations:")
    controller.write_file("demo_dir/README.md", "# JEDI Terminal Control\n\nTesting terminal capabilities.")
    print(f"   Created README.md")
    print(f"   Contents: {controller.read_file('demo_dir/README.md').strip()}")
    
    # Test command execution
    print("\n3. Command execution:")
    result = controller.execute_bash_command("pwd && ls -la")
    print(f"   Command output:")
    for line in result.stdout.split('\n')[:5]:
        print(f"     {line}")
    
    # Test system info
    print("\n4. System info:")
    sysinfo = controller.get_system_info()
    print(f"   System info (first 300 chars): {sysinfo[:300]}...")
    
    print("\n=== Demo Complete ===")
