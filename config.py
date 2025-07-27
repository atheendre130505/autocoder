# config.py
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class SafetyConfig:
    """Configuration for autonomous execution safety controls"""
    max_execution_time: int = 30  # Maximum seconds for command execution
    max_memory_mb: int = 512      # Maximum memory usage in MB
    max_iterations: int = 5       # Maximum retry attempts for fixing errors
    max_file_size_mb: int = 10    # Maximum size for generated files
    
    # Commands that require human approval
    require_approval_for: List[str] = field(default_factory=lambda: [
        "pip install", "git push", "git commit", "rm", "del", "sudo"
    ])
    
    # Directories where AI can operate safely
    allowed_directories: List[str] = field(default_factory=lambda: [
        "ai_workspace", "generated_code", "temp"
    ])
    
    # Network access controls
    allow_network_access: bool = False
    allowed_domains: List[str] = field(default_factory=lambda: [
        "pypi.org", "github.com", "api.github.com"
    ])

@dataclass  
class AgentConfig:
    """Configuration for AI agents and their capabilities"""
    # API Keys
    gemini_api_key: str = field(default_factory=lambda: os.getenv('GEMINI_API_KEY', ''))
    fireworks_api_key: str = field(default_factory=lambda: os.getenv('FIREWORKS_API_KEY', ''))
    github_token: str = field(default_factory=lambda: os.getenv('GITHUB_API_TOKEN', ''))
    
    # Model configurations
    planner_model: str = "gemini-2.0-flash-exp"
    coder_model: str = "accounts/fireworks/models/qwen3-coder-480b-a35b-instruct"
    
    # Agent behavior settings
    max_context_length: int = 100000
    temperature: float = 0.1
    max_tokens: int = 4000
    
    # Workspace settings
    workspace_dir: str = "ai_workspace"
    generated_code_dir: str = "generated_code"
    logs_dir: str = "logs"

@dataclass
class SystemConfig:
    """Main system configuration combining all settings"""
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    agents: AgentConfig = field(default_factory=AgentConfig)
    
    # System-wide settings
    debug_mode: bool = False
    verbose_logging: bool = True
    auto_save: bool = True
    
    def validate(self) -> List[str]:
        """Validate configuration and return any errors"""
        errors = []
        
        if not self.agents.gemini_api_key:
            errors.append("GEMINI_API_KEY environment variable not set")
        if not self.agents.fireworks_api_key:
            errors.append("FIREWORKS_API_KEY environment variable not set")
        if not self.agents.github_token:
            errors.append("GITHUB_API_TOKEN environment variable not set")
            
        if self.safety.max_execution_time <= 0:
            errors.append("max_execution_time must be positive")
        if self.safety.max_iterations <= 0:
            errors.append("max_iterations must be positive")
            
        return errors
    
    def create_directories(self) -> None:
        """Create necessary directories if they don't exist"""
        directories = [
            self.agents.workspace_dir,
            self.agents.generated_code_dir, 
            self.agents.logs_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")

# Global configuration instance
config = SystemConfig()

# Utility functions
def load_config() -> SystemConfig:
    """Load and validate system configuration"""
    global config
    config.create_directories()
    
    errors = config.validate()
    if errors:
        print("⚠️  Configuration errors found:")
        for error in errors:
            print(f"   - {error}")
        print("\nPlease fix these issues before running autonomous mode.")
    else:
        print("✅ Configuration validated successfully")
    
    return config

def get_config() -> SystemConfig:
    """Get the current system configuration"""
    return config

if __name__ == "__main__":
    # Test configuration when run directly
    print("Testing configuration...")
    test_config = load_config()
    print(f"Workspace directory: {test_config.agents.workspace_dir}")
    print(f"Safety level: max {test_config.safety.max_iterations} iterations")
    print(f"Models: {test_config.agents.planner_model} + {test_config.agents.coder_model}")
