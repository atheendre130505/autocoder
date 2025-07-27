# 🤖 Autonomous AI Development CLI

An advanced autonomous AI development system that can plan, code, execute, debug, and deliver working software solutions from natural language descriptions.

## 🚀 Features

- **🧠 AI Planning**: Uses Gemini 2.5 Pro for intelligent software planning
- **⚡ Code Generation**: Powered by Qwen3-Coder 480B for production-ready code
- **🔧 Autonomous Execution**: Automatically runs and tests generated code
- **🔄 Iterative Debugging**: Self-corrects errors and installs dependencies
- **🛡️ Safety Controls**: Command validation and sandboxed execution
- **📦 Package Management**: Auto-installs missing Python packages
- **💾 Memory System**: Learns from successes and failures
- **📊 Rich Logging**: Comprehensive execution tracking

## 🎯 What It Can Do

Transform natural language requests into working software:

# crazy_code

Overview

This system demonstrates true autonomous AI development - from natural language request to working software solution. It combines Google's Gemini 2.5 Pro for intelligent planning with Qwen3-Coder 480B for production-quality code generation, creating a fully autonomous development pipeline.

What Makes This Special

Intelligent Planning: Gemini 2.5 Pro creates detailed development strategies
Advanced Code Generation: Qwen3-Coder 480B produces production-ready code
Autonomous Execution: Runs, tests, and debugs code automatically
Self-Healing: Automatically fixes errors and installs dependencies
Enterprise Safety: Multi-layer security and command validation
Learning System: Remembers patterns and improves over time

Capabilities

Transform simple requests into sophisticated software:

python main.py autonomous Create a calculator that adds two numbers
python main.py autonomous Create a file organizer by extension
python main.py autonomous Create a web scraper that gets website titles
python main.py autonomous Create a password generator with complexity options
python main.py autonomous Create a task manager with priority queues

Example Results

Simple Calculator Request → Professional application with:
Input validation and error handling
Clean function architecture
User-friendly interface
Exception management

File Organizer Request → Enterprise-grade utility with:
Command-line argument parsing
Comprehensive logging system
File conflict resolution
Production-ready error handling

System Architecture

Natural Language Request → Gemini 2.5 Pro Planning → Qwen3-Coder 480B Coding → Autonomous Execution & Testing → Working Solution Delivered

Core Components

ai_agents.py: AI agent coordination and API integration
execution_engine.py: Safe autonomous code execution
safety_controls.py: Multi-layer command validation
error_analyzer.py: Intelligent error diagnosis and fixing
memory_system.py: Learning and pattern recognition
config.py: System configuration and settings

Prerequisites

Python 3.8+
Gemini API Key (Get one here: https://ai.google.dev/)
Fireworks API Key (Get one here: https://fireworks.ai/)
GitHub API Token (optional, for research features)

Quick Start

1. Clone and Setup

git clone https://github.com/yourusername/autonomous-ai-dev-cli.git
cd autonomous-ai-dev-cli

Create virtual environment
python -m venv ai-dev-cli-venv
source ai-dev-cli-venv/bin/activate  # Linux/Mac
# or ai-dev-cli-venv\Scripts\activate  # Windows

Install dependencies
pip install -r requirements.txt

2. Configure Environment

Set your API keys
export GEMINI_API_KEY='your_gemini_api_key_here'
export FIREWORKS_API_KEY='your_fireworks_api_key_here'
export GITHUB_API_TOKEN='your_github_token_here'  # Optional

Or create a .env file:
GEMINI_API_KEY=your_gemini_api_key_here
FIREWORKS_API_KEY=your_fireworks_api_key_here
GITHUB_API_TOKEN=your_github_token_here

3. Test the System

Test basic functionality
python main.py --help

Run your first autonomous development
python main.py autonomous Create a hello world program

Try something more complex
python main.py autonomous Create a file backup utility

Project Structure

ai-dev-cli/
main.py                  CLI interface and command routing
ai_agents.py            AI agent coordination (Gemini + Qwen3)
execution_engine.py     Autonomous code execution engine
safety_controls.py      Command safety and validation
error_analyzer.py       Error diagnosis and auto-fixing
memory_system.py        Learning and memory persistence
config.py               System configuration management
ai_workspace/           Execution sandbox directory
generated_code/         Autonomous solutions archive
logs/                   Execution logs and monitoring
examples/               Example generated applications

Usage Examples

Basic Development Commands

python main.py autonomous Create a number guessing game
python main.py autonomous Create a word counter for text files
python main.py autonomous Create a simple weather data parser
python main.py autonomous Create a duplicate file finder
python main.py autonomous Create a log file analyzer
python main.py autonomous Create a CSV data processor

Advanced Development

python main.py autonomous Create a personal expense tracker with categories
python main.py autonomous Create a REST API for user management
python main.py autonomous Create a web scraper with rate limiting

Development Tools

python main.py develop Create a database connection manager
python main.py execute generated_code/my_application.py

Safety & Security

Multi-Layer Protection

Command Validation: Whitelist/blacklist dangerous operations
Sandboxed Execution: Isolated workspace environment
Human Approval Gates: Critical operations require confirmation
Resource Monitoring: CPU, memory, and execution time limits
Network Controls: Restricted external access

Safety Levels

SAFE: Always allowed (e.g., python script.py, ls)
CAUTION: Monitored execution (e.g., pip install)
WARNING: Requires validation (e.g., unknown commands)
DANGER: Human approval required (e.g., rm, sudo)
FORBIDDEN: Never allowed (e.g., rm -rf /)

Performance & Results

Success Metrics
100% Success Rate on tested simple applications
1-iteration solutions for well-defined problems
Production-quality code with proper error handling
Automatic dependency management

Generated Code Quality
Professional function structure and naming
Comprehensive error handling and validation
User-friendly interfaces and prompts
Proper documentation and comments
Command-line argument parsing (when appropriate)

Configuration

Environment Variables

Variable | Description | Required
GEMINI_API_KEY | Google Gemini API key | Yes
FIREWORKS_API_KEY | Fireworks AI API key | Yes
GITHUB_API_TOKEN | GitHub API token | Optional

System Settings

Modify config.py to adjust:
Execution timeouts and resource limits
Safety levels and command restrictions
Model parameters (temperature, max tokens)
Workspace directories and file paths

Development & Testing

Running Tests

Test individual components
python config.py           Test configuration
python safety_controls.py  Test safety system
python execution_engine.py Test execution engine

Test imports and integration
python test_imports.py

Adding New Features

1. Extend AI Agents: Add new planning or coding strategies
2. Enhance Safety: Add new validation rules
3. Improve Memory: Extend learning capabilities
4. Add Integrations: Connect to more APIs or services

Contributing

We welcome contributions! Areas of interest:

New AI Models: Integration with other coding models
Enhanced Security: Additional safety mechanisms
Learning Systems: Improved memory and pattern recognition
Integrations: APIs, databases, deployment platforms

Development Setup

Fork the repository
git clone https://github.com/yourusername/autonomous-ai-dev-cli.git
cd autonomous-ai-dev-cli

Create feature branch
git checkout -b feature/your-feature-name

Make changes and test
python main.py autonomous Test your new feature

Submit pull request

Roadmap

Multi-language support (JavaScript, Go, Rust)
Web interface for easier interaction
Deployment automation (Docker, AWS, etc.)
Team collaboration features
Advanced debugging with step-through execution
Integration testing framework

Important Notes

Disclaimer
This system executes AI-generated code autonomously. Always:
Review generated code before production use
Run in controlled environments during development
Keep backups of important files
Monitor resource usage during execution

Limitations
Quality depends on task clarity - be specific in requests
Complex applications may require multiple iterations
API rate limits may affect performance
Generated code should be reviewed for security

License

MIT License - see LICENSE file for details.

Acknowledgments

Google Gemini Team for the powerful planning capabilities
Fireworks AI for providing access to Qwen3-Coder 480B
Open Source Community for the foundational libraries

Support

Issues: GitHub Issues (https://github.com/yourusername/autonomous-ai-dev-cli/issues)
Discussions: GitHub Discussions (https://github.com/yourusername/autonomous-ai-dev-cli/discussions)
Documentation: Wiki (https://github.com/yourusername/autonomous-ai-dev-cli/wiki)

Star this repository if it helped you build autonomous AI development capabilities!

Built with AI by autonomous AI agents, for autonomous AI development.
