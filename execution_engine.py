# execution_engine.py
import subprocess
import os
import time
import psutil
import signal
import threading
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import tempfile
import sys

from config import get_config
from safety_controls import validate_command, RiskLevel

@dataclass
class ExecutionResult:
    """Result of command or code execution"""
    command: str
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    error_type: Optional[str] = None
    suggested_fixes: List[str] = field(default_factory=list)
    resource_usage: Dict[str, Any] = field(default_factory=dict)

class ExecutionTimeout(Exception):
    """Raised when execution exceeds time limit"""
    pass

class AutonomousExecutor:
    """Core execution engine for autonomous AI agents"""
    
    def __init__(self, workspace_dir: str = None, agent_name: str = "ai_agent"):
        self.config = get_config()
        self.workspace_dir = Path(workspace_dir or self.config.agents.workspace_dir)
        self.agent_name = agent_name
        self.execution_history: List[ExecutionResult] = []
        
        # Ensure workspace exists
        self.workspace_dir.mkdir(exist_ok=True)
        
        # Set up logging
        self.log_file = Path(self.config.agents.logs_dir) / f"{agent_name}_execution.log"
        
        print(f"🤖 AutonomousExecutor initialized for {agent_name}")
        print(f"📁 Workspace: {self.workspace_dir}")
        print(f"📝 Logging to: {self.log_file}")

    def execute_command(self, command: str, context: str = "", timeout: int = None) -> ExecutionResult:
        """
        Execute a CLI command with safety checks and monitoring
        
        Args:
            command: The command to execute
            context: Context about why this command is being run
            timeout: Maximum execution time (uses config default if None)
            
        Returns:
            ExecutionResult with detailed execution information
        """
        start_time = time.time()
        timeout = timeout or self.config.safety.max_execution_time
        
        # Log the execution attempt
        self._log_execution_attempt(command, context)
        
        # Safety validation
        safety_verdict = validate_command(command, context)
        
        if not safety_verdict.allowed:
            return ExecutionResult(
                command=command,
                stdout="",
                stderr=f"Command blocked by safety controls: {safety_verdict.reason}",
                exit_code=-1,
                execution_time=0,
                success=False,
                error_type="SAFETY_VIOLATION"
            )
        
        if safety_verdict.requires_approval:
            if not self._request_human_approval(command, safety_verdict.reason):
                return ExecutionResult(
                    command=command,
                    stdout="",
                    stderr="Command execution denied by user",
                    exit_code=-2,
                    execution_time=0,
                    success=False,
                    error_type="USER_DENIED"
                )
        
        # Execute the command
        try:
            result = self._execute_with_monitoring(command, timeout)
            execution_time = time.time() - start_time
            
            # Create execution result
            exec_result = ExecutionResult(
                command=command,
                stdout=result['stdout'],
                stderr=result['stderr'],
                exit_code=result['exit_code'],
                execution_time=execution_time,
                success=result['exit_code'] == 0,
                resource_usage=result.get('resource_usage', {})
            )
            
            # Analyze errors if command failed
            if not exec_result.success:
                exec_result.error_type = self._classify_error(exec_result.stderr)
                exec_result.suggested_fixes = self._suggest_error_fixes(exec_result.stderr, command)
            
            # Store in history
            self.execution_history.append(exec_result)
            self._log_execution_result(exec_result)
            
            return exec_result
            
        except ExecutionTimeout:
            return ExecutionResult(
                command=command,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                exit_code=-3,
                execution_time=timeout,
                success=False,
                error_type="TIMEOUT"
            )
        except Exception as e:
            return ExecutionResult(
                command=command,
                stdout="",
                stderr=f"Execution error: {str(e)}",
                exit_code=-4,
                execution_time=time.time() - start_time,
                success=False,
                error_type="EXECUTION_ERROR"
            )

    def execute_python_code(self, code: str, filename: str = None, timeout: int = None) -> ExecutionResult:
        """
        Execute Python code in the workspace with monitoring
        
        Args:
            code: Python code to execute
            filename: Optional filename to save code as
            timeout: Maximum execution time in seconds
            
        Returns:
            ExecutionResult with execution details
        """
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"auto_generated_{timestamp}.py"
        
        # Ensure .py extension
        if not filename.endswith('.py'):
            filename += '.py'
        
        # Save code to file in workspace
        code_file = self.workspace_dir / filename
        
        try:
            # Create any necessary parent directories
            code_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save the code to file
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            print(f"💾 Code saved to: {code_file}")
            
            # Execute using just the filename since we change to workspace directory
            python_cmd = f"python3 {filename}"  # Using python3 explicitly for Linux
            result = self.execute_command(
                command=python_cmd,
                context=f"Executing generated Python code: {filename}",
                timeout=timeout
            )
            
            # Add additional context to the result if needed
            if not result.success and result.error_type == "UNKNOWN_ERROR":
                result.error_type = self._classify_error(result.stderr)
                result.suggested_fixes = self._suggest_error_fixes(result.stderr, python_cmd)
            
            return result
            
        except Exception as e:
            error_msg = f"Error saving/executing Python code: {str(e)}"
            print(f"❌ {error_msg}")
            
            return ExecutionResult(
                command=f"python3 {filename}",
                stdout="",
                stderr=error_msg,
                exit_code=-5,
                execution_time=0,
                success=False,
                error_type="PYTHON_EXECUTION_ERROR",
                suggested_fixes=["Check file permissions", "Verify Python installation"]
            )

    def install_package(self, package_name: str, version: str = None) -> ExecutionResult:
        """
        Safely install a Python package
        
        Args:
            package_name: Name of the package to install
            version: Optional version specification
            
        Returns:
            ExecutionResult with installation details
        """
        # Build pip install command
        if version:
            command = f"pip install {package_name}=={version}"
        else:
            command = f"pip install {package_name}"
        
        # Execute with package installation context
        context = f"Installing Python package: {package_name}"
        if version:
            context += f" (version {version})"
        
        return self.execute_command(command, context, timeout=120)  # Longer timeout for installations

    def _execute_with_monitoring(self, command: str, timeout: int) -> Dict[str, Any]:
        """Execute command with resource monitoring"""
        # Change to workspace directory
        original_cwd = os.getcwd()
        os.chdir(self.workspace_dir)
        
        try:
            # Start the process
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            # Monitor execution with timeout
            stdout_data = []
            stderr_data = []
            start_time = time.time()
            
            # Use communicate with timeout
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                
                return {
                    'stdout': stdout,
                    'stderr': stderr,
                    'exit_code': process.returncode,
                    'resource_usage': self._get_resource_usage()
                }
                
            except subprocess.TimeoutExpired:
                # Kill the process group
                if os.name != 'nt':
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()
                process.wait()
                raise ExecutionTimeout(f"Command '{command}' timed out after {timeout} seconds")
                
        finally:
            # Restore original directory
            os.chdir(original_cwd)

    def _request_human_approval(self, command: str, reason: str) -> bool:
        """Request human approval for dangerous commands"""
        print(f"\n🚨 HUMAN APPROVAL REQUIRED 🚨")
        print(f"Command: {command}")
        print(f"Reason: {reason}")
        print(f"Agent: {self.agent_name}")
        
        while True:
            response = input("\nApprove this command? (yes/no/details): ").lower().strip()
            
            if response in ['yes', 'y']:
                print("✅ Command approved by human")
                return True
            elif response in ['no', 'n']:
                print("❌ Command denied by human")
                return False
            elif response in ['details', 'd']:
                print(f"\nCommand details:")
                print(f"  Command: {command}")
                print(f"  Safety concern: {reason}")
                print(f"  Requesting agent: {self.agent_name}")
                print(f"  Workspace: {self.workspace_dir}")
                continue
            else:
                print("Please respond with 'yes', 'no', or 'details'")

    def _classify_error(self, stderr: str) -> str:
        """Classify the type of error from stderr"""
        stderr_lower = stderr.lower()
        
        if 'modulenotfounderror' in stderr_lower or 'no module named' in stderr_lower:
            return 'MISSING_MODULE'
        elif 'syntaxerror' in stderr_lower:
            return 'SYNTAX_ERROR'
        elif 'indentationerror' in stderr_lower:
            return 'INDENTATION_ERROR'
        elif 'nameerror' in stderr_lower:
            return 'NAME_ERROR'
        elif 'typeerror' in stderr_lower:
            return 'TYPE_ERROR'
        elif 'valueerror' in stderr_lower:
            return 'VALUE_ERROR'
        elif 'filenotfounderror' in stderr_lower:
            return 'FILE_NOT_FOUND'
        elif 'permissionerror' in stderr_lower:
            return 'PERMISSION_ERROR'
        else:
            return 'UNKNOWN_ERROR'

    def _suggest_error_fixes(self, stderr: str, command: str) -> List[str]:
        """Suggest fixes for common errors"""
        fixes = []
        error_type = self._classify_error(stderr)
        
        if error_type == 'MISSING_MODULE':
            # Extract module name from error
            import re
            match = re.search(r"No module named '([^']+)'", stderr)
            if match:
                module = match.group(1)
                fixes.append(f"Install missing module: pip install {module}")
        
        elif error_type == 'SYNTAX_ERROR':
            fixes.append("Check Python syntax - look for missing colons, parentheses, or quotes")
            fixes.append("Verify indentation is consistent")
        
        elif error_type == 'INDENTATION_ERROR':
            fixes.append("Fix indentation - use consistent spaces or tabs")
            fixes.append("Check that code blocks are properly indented")
        
        elif error_type == 'FILE_NOT_FOUND':
            fixes.append("Check that the file path is correct")
            fixes.append("Ensure the file exists in the expected location")
        
        elif error_type == 'PERMISSION_ERROR':
            fixes.append("Check file permissions")
            fixes.append("Ensure you have write access to the target directory")
        
        return fixes

    def _get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage"""
        try:
            process = psutil.Process()
            return {
                'cpu_percent': process.cpu_percent(),
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'num_threads': process.num_threads()
            }
        except:
            return {}

    def _log_execution_attempt(self, command: str, context: str):
        """Log execution attempt"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent': self.agent_name,
            'action': 'EXECUTION_ATTEMPT',
            'command': command,
            'context': context
        }
        self._write_log(log_entry)

    def _log_execution_result(self, result: ExecutionResult):
        """Log execution result"""
        log_entry = {
            'timestamp': result.timestamp.isoformat(),
            'agent': self.agent_name,
            'action': 'EXECUTION_RESULT',
            'command': result.command,
            'success': result.success,
            'exit_code': result.exit_code,
            'execution_time': result.execution_time,
            'error_type': result.error_type
        }
        self._write_log(log_entry)

    def _write_log(self, log_entry: Dict[str, Any]):
        """Write log entry to file"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")

    def get_execution_history(self) -> List[ExecutionResult]:
        """Get history of all executions"""
        return self.execution_history.copy()

    def clear_history(self):
        """Clear execution history"""
        self.execution_history.clear()
        print(f"🧹 Execution history cleared for {self.agent_name}")

if __name__ == "__main__":
    # Test the execution engine
    print("Testing Autonomous Execution Engine...")
    
    executor = AutonomousExecutor(agent_name="test_agent")
    
    # Test safe command
    print("\n1. Testing safe command:")
    result = executor.execute_command("echo 'Hello from AI agent!'")
    print(f"Success: {result.success}")
    print(f"Output: {result.stdout.strip()}")
    
    # Test Python code execution
    print("\n2. Testing Python code execution:")
    python_code = """
print("Hello from generated Python code!")
import math
print(f"Pi is approximately {math.pi:.4f}")
for i in range(3):
    print(f"Count: {i}")
"""
    result = executor.execute_python_code(python_code, "test_script.py")
    print(f"Success: {result.success}")
    print(f"Output: {result.stdout}")
    
    # Test package installation (safe package)
    print("\n3. Testing package installation:")
    result = executor.install_package("requests")
    print(f"Success: {result.success}")
    if result.success:
        print("✅ Package installed successfully")
    else:
        print(f"❌ Installation failed: {result.stderr}")
    
    print(f"\n📊 Total executions: {len(executor.get_execution_history())}")
