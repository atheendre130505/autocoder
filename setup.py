#!/usr/bin/env python3
"""
Setup script for autocoder.
Handles installation and configuration.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment configuration."""
    print("🔧 Setting up environment...")
    
    env_file = Path(".env")
    env_template = Path(".env.template")
    
    if not env_file.exists():
        if env_template.exists():
            shutil.copy(env_template, env_file)
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your API keys")
        else:
            print("❌ .env.template not found")
            return False
    else:
        print("✅ .env file already exists")
    
    return True

def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    
    directories = ["logs", "projects", "temp"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ {directory}/")
    
    return True

def test_installation():
    """Test the installation."""
    print("🧪 Testing installation...")
    
    try:
        # Test imports
        from agents.gemini_agent import GeminiAgent
        from agents.qwen_agent import QwenAgent
        from cli.interface import AutocoderCLI
        from core import config
        
        print("✅ All modules imported successfully")
        
        # Test configuration
        config_status = config.validate_config()
        print(f"✅ Configuration loaded")
        print(f"   - Gemini API: {'✓' if config_status.get('gemini_key_present') else '✗'}")
        print(f"   - Fireworks API: {'✓' if config_status.get('fireworks_key_present') else '✗'}")
        print(f"   - GitHub API: {'✓' if config_status.get('github_token_present') else '✗'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Autocoder Setup")
    print("=" * 50)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Setting up environment", setup_environment),
        ("Creating directories", create_directories),
        ("Testing installation", test_installation)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: python main.py")
    print("3. Or run tests: python test_autocoder.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
