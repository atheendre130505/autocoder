import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration management for the autocoder project."""
    
    def __init__(self):
        # API Keys
        self.GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
        self.FIREWORKS_API_KEY = os.getenv('FIREWORKS_API_KEY', '')
        self.GITHUB_API_TOKEN = os.getenv('GITHUB_API_TOKEN', '')
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
        
        # Project Settings
        self.PROJECT_ROOT = os.getcwd()
        self.PLAN_FILE = 'planfile.txt'
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        
        # Agent Settings
        self.GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        self.QWEN_MODEL = os.getenv('QWEN_MODEL', 'accounts/fireworks/models/qwen3-coder-480b-a35b-instruct')
        self.FIREWORKS_BASE_URL = 'https://api.fireworks.ai/inference/v1'
        self.MAX_CONTEXT_LENGTH = 8192  # Increased for better context
        
        # Safety Settings
        self.REQUIRE_APPROVAL = os.getenv('REQUIRE_APPROVAL', 'false').lower() == 'true'
        self.AUTO_SAVE_INTERVAL = 300  # seconds
        self.MAX_FILE_SIZE = 1024 * 1024  # 1MB
        
        # Autonomous Mode Settings
        self.AUTONOMOUS_MODE = os.getenv('AUTONOMOUS_MODE', 'true').lower() == 'true'
        self.AUTO_INSTALL_DEPS = os.getenv('AUTO_INSTALL_DEPS', 'true').lower() == 'true'
        self.AUTO_EXECUTE_PROJECTS = os.getenv('AUTO_EXECUTE_PROJECTS', 'true').lower() == 'true'
        self.MAX_EXECUTION_TIME = int(os.getenv('MAX_EXECUTION_TIME', '300'))  # 5 minutes
        
    # ... rest of the Config class remains the same

        
    def validate_config(self) -> Dict[str, bool]:
        """Validate configuration settings."""
        validation_results = {
            'gemini_key_present': bool(self.GEMINI_API_KEY),
            'fireworks_key_present': bool(self.FIREWORKS_API_KEY),
            'github_token_present': bool(self.GITHUB_API_TOKEN),
            'project_root_exists': os.path.exists(self.PROJECT_ROOT),
            'plan_file_writable': self._check_file_writable(self.PLAN_FILE)
        }
        return validation_results
    
    def _check_file_writable(self, filepath: str) -> bool:
        """Check if file is writable."""
        try:
            with open(filepath, 'a'):
                pass
            return True
        except (IOError, OSError):
            return False
    
    def get_config_summary(self) -> str:
        """Get a summary of current configuration."""
        validation = self.validate_config()
        
        summary = f"""
Configuration Summary:
- Project Root: {self.PROJECT_ROOT}
- Plan File: {self.PLAN_FILE}
- Log Level: {self.LOG_LEVEL}
- Require Approval: {self.REQUIRE_APPROVAL}

API Configuration:
- Gemini API Key: {'✓' if validation['gemini_key_present'] else '✗'}
- Fireworks API Key: {'✓' if validation['fireworks_key_present'] else '✗'}
- GitHub Token: {'✓' if validation['github_token_present'] else '✗'}

Model Settings:
- Gemini Model: {self.GEMINI_MODEL}
- Qwen Model: {self.QWEN_MODEL}
- Max Context: {self.MAX_CONTEXT_LENGTH}
"""
        return summary

# Global config instance
config = Config()
