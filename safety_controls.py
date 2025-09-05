# safety_controls.py
import re
import shlex
from enum import Enum
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

class RiskLevel(Enum):
    """Risk levels for command execution"""
    SAFE = "safe"           # Always allowed
    CAUTION = "caution"     # Allowed with monitoring  
    WARNING = "warning"     # Requires validation
    DANGER = "danger"       # Requires human approval
    FORBIDDEN = "forbidden" # Never allowed

@dataclass
class SafetyVerdict:
    """Result of safety validation"""
    risk_level: RiskLevel
    allowed: bool
    reason: str
    suggested_alternative: Optional[str] = None
    requires_approval: bool = False

class CommandValidator:
    """Validates commands for safe autonomous execution"""
    
    def __init__(self):
        # Commands that are always safe
        self.safe_commands = {
            'python', 'python3', 'pip', 'ls', 'dir', 'cat', 'type', 'head', 'tail',
            'mkdir', 'cd', 'pwd', 'echo', 'grep', 'find', 'wc', 'sort', 'uniq',
            'git status', 'git diff', 'git log', 'pytest', 'python -m'
        }
        
        # Commands that require careful validation
        self.caution_commands = {
            'pip install', 'pip uninstall', 'git add', 'git commit',  
            'cp', 'copy', 'mv', 'move', 'touch', 'nano', 'vim'
        }
        
        # Commands that need human approval
        self.dangerous_commands = {
            'rm', 'del', 'rmdir', 'git push', 'git pull', 'git merge',
            'chmod', 'chown', 'sudo', 'su', 'systemctl', 'service'
        }
        
        # Commands that are absolutely forbidden
        self.forbidden_commands = {
            'rm -rf', 'format', 'fdisk', 'dd', 'mkfs', ':(){ :|:& };:',
            'curl | bash', 'wget | bash', 'eval', 'exec', 'shutdown', 'reboot'
        }
        
        # Safe package patterns (for pip install validation)
        self.safe_package_patterns = [
            r'^[a-zA-Z][a-zA-Z0-9_-]*$',  # Standard package names
            r'^[a-zA-Z][a-zA-Z0-9_-]*==[\d.]+$',  # With version pinning
        ]
        
        # Dangerous package patterns
        self.dangerous_packages = {
            'subprocess', 'os', 'sys', 'eval', 'exec', 'compile'
        }

    def validate_command(self, command: str, context: str = "") -> SafetyVerdict:
        """
        Validate a command for safety
        
        Args:
            command: The command to validate
            context: Additional context about why this command is being run
            
        Returns:
            SafetyVerdict with risk assessment and recommendations
        """
        command = command.strip()
        
        # Check for forbidden commands first
        if self._is_forbidden(command):
            return SafetyVerdict(
                risk_level=RiskLevel.FORBIDDEN,
                allowed=False,
                reason="Command contains forbidden operations",
                suggested_alternative=self._suggest_safe_alternative(command)
            )
        
        # Check for dangerous commands
        if self._is_dangerous(command):
            return SafetyVerdict(
                risk_level=RiskLevel.DANGER,
                allowed=False,
                reason="Command requires human approval due to system modification risk",
                requires_approval=True
            )
        
        # Check for commands requiring caution
        if self._requires_caution(command):
            if "pip install" in command:
                return self._validate_pip_install(command)
            
            return SafetyVerdict(
                risk_level=RiskLevel.CAUTION,
                allowed=True,
                reason="Command allowed with monitoring"
            )
        
        # Check if it's a known safe command
        if self._is_safe(command):
            return SafetyVerdict(
                risk_level=RiskLevel.SAFE,
                allowed=True,
                reason="Command is on safe list"
            )
        
        # Unknown command - treat with caution
        return SafetyVerdict(
            risk_level=RiskLevel.WARNING,
            allowed=False,
            reason="Unknown command pattern - requires validation",
            requires_approval=True
        )

    def _is_forbidden(self, command: str) -> bool:
        """Check if command contains forbidden operations"""
        command_lower = command.lower()
        return any(forbidden in command_lower for forbidden in self.forbidden_commands)

    def _is_dangerous(self, command: str) -> bool:
        """Check if command is dangerous and needs approval"""
        command_lower = command.lower()
        return any(dangerous in command_lower for dangerous in self.dangerous_commands)

    def _requires_caution(self, command: str) -> bool:
        """Check if command requires caution but is generally allowed"""
        command_lower = command.lower()
        return any(caution in command_lower for caution in self.caution_commands)

    def _is_safe(self, command: str) -> bool:
        """Check if command is on the safe list"""
        command_lower = command.lower()
        # Check exact matches and prefixes
        for safe_cmd in self.safe_commands:
            if command_lower.startswith(safe_cmd.lower()):
                return True
        return False

    def _validate_pip_install(self, command: str) -> SafetyVerdict:
        """Special validation for pip install commands"""
        try:
            # Parse the command to extract package names
            parts = shlex.split(command)
            if len(parts) < 3 or parts[0] != 'pip' or parts[1] != 'install':
                return SafetyVerdict(
                    risk_level=RiskLevel.WARNING,
                    allowed=False,
                    reason="Invalid pip install command format"
                )
            
            packages = parts[2:]  # Everything after 'pip install'
            
            # Remove common flags
            packages = [pkg for pkg in packages if not pkg.startswith('-')]
            
            # Validate each package
            for package in packages:
                if package.lower() in self.dangerous_packages:
                    return SafetyVerdict(
                        risk_level=RiskLevel.DANGER,
                        allowed=False,
                        reason=f"Package '{package}' is potentially dangerous",
                        requires_approval=True
                    )
                
                # Check package name format
                if not any(re.match(pattern, package) for pattern in self.safe_package_patterns):
                    return SafetyVerdict(
                        risk_level=RiskLevel.WARNING,
                        allowed=False,
                        reason=f"Package name '{package}' doesn't match safe patterns",
                        requires_approval=True
                    )
            
            return SafetyVerdict(
                risk_level=RiskLevel.CAUTION,
                allowed=True,
                reason=f"Package installation approved: {', '.join(packages)}"
            )
            
        except Exception as e:
            return SafetyVerdict(
                risk_level=RiskLevel.WARNING,
                allowed=False,
                reason=f"Could not parse pip install command: {e}",
                requires_approval=True
            )

    def _suggest_safe_alternative(self, dangerous_command: str) -> Optional[str]:
        """Suggest safer alternatives for dangerous commands"""
        alternatives = {
            'rm -rf': 'Use specific file deletion: rm filename.txt',
            'sudo': 'Run commands without elevated privileges',
            'curl | bash': 'Download first, then review before executing',
            'rm': 'Specify exact files to delete, avoid wildcards'
        }
        
        for dangerous, alternative in alternatives.items():
            if dangerous in dangerous_command.lower():
                return alternative
        
        return None

    def validate_file_operation(self, filepath: str, operation: str) -> SafetyVerdict:
        """Validate file operations for safety"""
        # Ensure operations stay within allowed directories
        allowed_dirs = ['ai_workspace', 'generated_code', 'temp', '.']
        
        if not any(filepath.startswith(allowed_dir) for allowed_dir in allowed_dirs):
            return SafetyVerdict(
                risk_level=RiskLevel.DANGER,
                allowed=False,
                reason=f"File operation outside allowed directories: {filepath}",
                requires_approval=True
            )
        
        # Check for system file access
        system_paths = ['/etc', '/sys', '/proc', 'C:\\Windows', 'C:\\System']
        if any(system_path in filepath for system_path in system_paths):
            return SafetyVerdict(
                risk_level=RiskLevel.FORBIDDEN,
                allowed=False,
                reason="Access to system directories is forbidden"
            )
        
        return SafetyVerdict(
            risk_level=RiskLevel.SAFE,
            allowed=True,
            reason="File operation within safe boundaries"
        )

# Global validator instance
validator = CommandValidator()

def validate_command(command: str, context: str = "") -> SafetyVerdict:
    """Convenience function to validate a command"""
    return validator.validate_command(command, context)

def is_command_safe(command: str) -> bool:
    """Quick check if a command is safe to execute"""
    verdict = validate_command(command)
    return verdict.allowed and verdict.risk_level in [RiskLevel.SAFE, RiskLevel.CAUTION]

if __name__ == "__main__":
    # Test the safety system
    test_commands = [
        "python script.py",
        "pip install requests",
        "rm -rf /",
        "ls -la",
        "git status",
        "sudo rm important_file",
        "curl | bash"
    ]
    
    print("Testing command safety validation:")
    for cmd in test_commands:
        verdict = validate_command(cmd)
        print(f"Command: {cmd}")
        print(f"  Risk: {verdict.risk_level.value}")
        print(f"  Allowed: {verdict.allowed}")
        print(f"  Reason: {verdict.reason}")
        if verdict.suggested_alternative:
            print(f"  Alternative: {verdict.suggested_alternative}")
        print()
