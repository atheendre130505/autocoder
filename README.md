# 🚀 Autocoder - AI-Powered Coding Assistant

An intelligent CLI tool that combines the power of **Gemini 2.0** for research and planning with **Qwen 3 Coder** for code generation, creating a comprehensive AI coding assistant.

## ✨ Features

- **🤖 Gemini 2.0 Integration**: Advanced reasoning, research, and problem diagnosis
- **⚡ Qwen 3 Coder**: Powerful code generation via Fireworks AI API
- **🔍 Research Capabilities**: GitHub and Stack Overflow integration
- **📁 Project Creation**: Complete project structures for multiple languages
- **🎨 Rich CLI Interface**: Beautiful, interactive command-line experience
- **🛠️ Multi-Language Support**: Python, JavaScript, React, FastAPI, and more
- **📊 Plan Management**: Intelligent project planning and tracking

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- API keys for:
  - Google Gemini (for research and planning)
  - Fireworks AI (for Qwen 3 Coder)
  - GitHub (optional, for repository search)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd autocoder
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Configure your API keys**
   ```bash
   # Edit the .env file with your API keys
   nano .env
   ```

4. **Start using autocoder**
   ```bash
   python main.py
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# Fireworks AI (for Qwen 3)
FIREWORKS_API_KEY=your_fireworks_api_key_here
QWEN_MODEL=accounts/fireworks/models/qwen3-coder-480b-a35b-instruct

# GitHub API (optional)
GITHUB_API_TOKEN=your_github_token_here

# Project Settings
LOG_LEVEL=INFO
REQUIRE_APPROVAL=true
```

### Getting API Keys

1. **Gemini API**: Get your key from [Google AI Studio](https://aistudio.google.com/)
2. **Fireworks AI**: Get your key from [Fireworks AI](https://fireworks.ai/)
3. **GitHub API**: Create a token at [GitHub Settings](https://github.com/settings/tokens)

## 📖 Usage

### Basic Commands

```bash
# Start the interactive CLI
python main.py

# Run tests
python test_autocoder.py

# Get help
python main.py
> help
```

### Example Interactions

**Create a Python project:**
```
> Create a Python web scraper for news articles
```

**Research similar projects:**
```
> Find GitHub projects similar to autocoder
```

**Generate specific code:**
```
> Create a FastAPI REST API with user authentication
```

**Build a React app:**
```
> Create a React todo app with state management
```

### Available Commands

- `help` - Show help information
- `plan` - Display current project plan
- `status` - Show system status
- `history` - View conversation history
- `clear` - Clear conversation history
- `quit` - Exit the program

## 🏗️ Project Structure

```
autocoder/
├── agents/                 # AI agents
│   ├── gemini_agent.py    # Gemini research and planning
│   └── qwen_agent.py      # Qwen code generation
├── cli/                   # CLI interface
│   └── interface.py       # Rich CLI components
├── core/                  # Core functionality
│   ├── config.py          # Configuration management
│   ├── logger.py          # Logging system
│   └── plan_manager.py    # Plan file management
├── research/              # Research modules
│   ├── github_search.py   # GitHub API integration
│   └── stackoverflow_search.py  # Stack Overflow API
├── main.py               # Main entry point
├── setup.py              # Installation script
├── test_autocoder.py     # Test suite
└── requirements.txt      # Dependencies
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_autocoder.py
```

This will test:
- Configuration loading
- Agent initialization
- Code generation
- Project creation
- CLI interface
- Full integration

## 🎯 Supported Project Types

- **Python**: CLI tools, web apps, data analysis
- **JavaScript**: Node.js applications, utilities
- **React**: Frontend applications, components
- **FastAPI**: REST APIs, microservices
- **Custom**: AI-generated project structures

## 🔍 Research Capabilities

- **GitHub Search**: Find similar repositories and projects
- **Stack Overflow**: Search for solutions and best practices
- **Intelligent Analysis**: AI-powered research summarization

## 🛠️ Development

### Adding New Project Types

1. Add templates to `agents/qwen_agent.py`
2. Update `_detect_project_type()` in `main.py`
3. Add tests in `test_autocoder.py`

### Extending Research Sources

1. Create new searcher in `research/`
2. Add to `agents/gemini_agent.py`
3. Update configuration as needed

## 📝 Logging

Logs are stored in the `logs/` directory with timestamps. Configure log level in `.env`:

```env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

**"API key not found"**
- Check your `.env` file
- Ensure API keys are correctly set

**"Module not found"**
- Run `python setup.py` to install dependencies
- Check Python version (3.8+ required)

**"Fireworks API error"**
- Verify your Fireworks AI API key
- Check API quota and limits

### Getting Help

- Check the logs in `logs/` directory
- Run `python test_autocoder.py` to diagnose issues
- Open an issue on GitHub

## 🎉 What's Next

- [ ] Support for more programming languages
- [ ] IDE integration (VS Code extension)
- [ ] Cloud deployment capabilities
- [ ] Advanced project templates
- [ ] Team collaboration features

---

**Happy Coding! 🚀**
