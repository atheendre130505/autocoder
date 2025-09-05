import logging
import os
from datetime import datetime
from typing import Optional

class AutocoderLogger:
    """Custom logger for the autocoder project."""
    
    def __init__(self, name: str = 'autocoder', log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Set default log file if none provided
        if log_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = f'logs/autocoder_{timestamp}.log'
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers if they don't exist
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def log_plan_update(self, update_type: str, details: str) -> None:
        """Log plan-specific updates."""
        self.info(f"PLAN_UPDATE - {update_type}: {details}")
    
    def log_agent_action(self, agent: str, action: str, details: str) -> None:
        """Log agent-specific actions."""
        self.info(f"AGENT_ACTION - {agent} - {action}: {details}")

# Global logger instance
logger = AutocoderLogger()
