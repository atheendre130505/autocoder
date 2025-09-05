"""
Core module for Autocoder project.
Provides plan management, configuration, and logging functionality.
"""

from .plan_manager import PlanManager
from .config import config, Config
from .logger import logger, AutocoderLogger

__all__ = ['PlanManager', 'config', 'Config', 'logger', 'AutocoderLogger']
__version__ = '0.1.0'
