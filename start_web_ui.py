#!/usr/bin/env python3
"""
Startup script for the Autocoder Web UI
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import flask
        import flask_socketio
        from agents.gemini_agent import GeminiAgent
        from agents.qwen_agent import QwenAgent
        from core import config
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_config():
    """Check if configuration is properly set up."""
    from core import config
    
    print("🔧 Checking configuration...")
    
    # Check API keys
    if not config.GEMINI_API_KEY:
        print("⚠️  Warning: GEMINI_API_KEY not set")
    else:
        print("✅ Gemini API key configured")
    
    if not config.FIREWORKS_API_KEY:
        print("⚠️  Warning: FIREWORKS_API_KEY not set")
    else:
        print("✅ Fireworks API key configured")
    
    if not config.GITHUB_API_TOKEN:
        print("⚠️  Warning: GITHUB_API_TOKEN not set (optional)")
    else:
        print("✅ GitHub API token configured")
    
    # Check autonomous mode
    if config.AUTONOMOUS_MODE:
        print("✅ Autonomous mode enabled")
    else:
        print("⚠️  Warning: Autonomous mode disabled")
    
    return True

def create_directories():
    """Create necessary directories."""
    directories = ['templates', 'static', 'projects', 'logs']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}/")

def main():
    """Main startup function."""
    print("🚀 Starting Autocoder Web UI")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check configuration
    check_config()
    
    # Create directories
    create_directories()
    
    print("\n🌐 Starting web server...")
    print("📱 Open your browser to: http://localhost:5000")
    print("🤖 Autonomous mode is enabled!")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 40)
    
    # Start the web UI
    try:
        from web_ui import app, socketio, init_autocoder
        
        # Initialize autocoder
        init_autocoder()
        
        # Run the app
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down web server...")
    except Exception as e:
        print(f"\n❌ Error starting web server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
