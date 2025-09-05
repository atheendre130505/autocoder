#!/usr/bin/env python3
"""
Simple terminal interface for Autocoder
Focus on terminal productivity and AI coding assistance
"""

import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.markdown import Markdown
from datetime import datetime

class TerminalInterface:
    """Simple terminal interface for Autocoder."""
    
    def __init__(self):
        self.console = Console()
        self.history = []
        
    def display_welcome(self):
        """Display welcome message."""
        welcome_text = """
# 🤖 **AUTOCODER - AI CODING ASSISTANT**

**Terminal-First AI Development Tool**

- **Gemini 2.5 Pro**: Research, planning, and problem analysis
- **Qwen3-Coder**: Advanced code generation and debugging
- **Autonomous Mode**: Create, code, debug, and execute projects

**Commands**: `help` | `create <description>` | `run <project>` | `debug <project>` | `list` | `status` | `quit`
        """
        
        self.console.print(Panel(
            Markdown(welcome_text),
            title="🚀 Welcome to Autocoder",
            border_style="blue",
            padding=(1, 2)
        ))
    
    def display_loading(self, message: str):
        """Display loading message."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            progress.add_task(description=message, total=None)
    
    def display_success(self, message: str):
        """Display success message."""
        self.console.print(f"✅ {message}", style="green")
    
    def display_error(self, message: str):
        """Display error message."""
        self.console.print(f"❌ {message}", style="red")
    
    def display_info(self, message: str):
        """Display info message."""
        self.console.print(f"ℹ️  {message}", style="blue")
    
    def display_separator(self):
        """Display separator line."""
        self.console.print("─" * 80, style="dim")
    
    def get_user_input(self) -> str:
        """Get user input with prompt."""
        return Prompt.ask("\n[bold blue]autocoder[/bold blue]")
    
    def display_help(self):
        """Display help information."""
        help_text = """
# 📖 **AUTOCODER COMMANDS**

## **Core Commands**
- `create <description>` - Create a new project from description
- `run <project>` - Execute a project
- `debug <project>` - Debug and fix project issues
- `list` - List all available projects
- `status` - Show system status and configuration

## **Utility Commands**
- `help` - Show this help message
- `history` - View conversation history
- `clear` - Clear conversation history
- `quit` - Exit the program

## **Examples**
```
create Python web scraper for news articles
create React todo app with state management
create FastAPI REST API with authentication
run my_calculator_project
debug my_web_scraper
list
status
```
        """
        
        self.console.print(Panel(
            Markdown(help_text),
            title="📖 Help",
            border_style="green"
        ))
    
    def display_status(self, config_status: dict, plan_content: str = ""):
        """Display system status."""
        status_table = Table(title="🔧 System Status")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="green")
        status_table.add_column("Details", style="white")
        
        # Add status rows
        for key, value in config_status.items():
            if isinstance(value, bool):
                status = "✅ Enabled" if value else "❌ Disabled"
                details = "Working" if value else "Not configured"
            else:
                status = "✅ Configured" if value else "❌ Missing"
                details = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            
            status_table.add_row(key.replace('_', ' ').title(), status, details)
        
        self.console.print(status_table)
        
        if plan_content:
            self.console.print(Panel(
                plan_content,
                title="📋 Current Plan",
                border_style="yellow"
            ))
    
    def display_projects(self, projects: list):
        """Display list of projects."""
        if not projects:
            self.console.print("📁 No projects found. Create your first project!")
            return
        
        project_table = Table(title="📁 Available Projects")
        project_table.add_column("Name", style="cyan")
        project_table.add_column("Type", style="green")
        project_table.add_column("Files", style="yellow")
        project_table.add_column("Created", style="blue")
        
        for project in projects:
            project_table.add_row(
                project.get('name', 'Unknown'),
                project.get('type', 'Unknown'),
                str(len(project.get('files', []))),
                project.get('timestamp', 'Unknown')[:10] if project.get('timestamp') else 'Unknown'
            )
        
        self.console.print(project_table)
    
    def display_code(self, code: str, language: str = "python"):
        """Display code with syntax highlighting."""
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        self.console.print(Panel(
            syntax,
            title=f"💻 Generated Code ({language})",
            border_style="green"
        ))
    
    def display_project_result(self, result: dict):
        """Display project creation result."""
        if result.get('success'):
            self.display_success(f"Project created successfully: {result.get('project_name', 'Unknown')}")
            
            if result.get('created_files'):
                self.console.print(f"📁 Created {len(result['created_files'])} files:")
                for file_path in result['created_files'][:5]:  # Show first 5 files
                    self.console.print(f"  • {file_path}")
                if len(result['created_files']) > 5:
                    self.console.print(f"  • ... and {len(result['created_files']) - 5} more files")
            
            if result.get('execution_info'):
                exec_info = result['execution_info']
                if exec_info.get('success'):
                    self.display_success("Project executed successfully!")
                else:
                    self.display_error(f"Execution failed: {exec_info.get('error', 'Unknown error')}")
        else:
            self.display_error(f"Project creation failed: {result.get('error', 'Unknown error')}")
    
    def display_history(self, history: list):
        """Display conversation history."""
        if not history:
            self.console.print("📝 No conversation history.")
            return
        
        self.console.print(Panel(
            "\n".join([f"{i+1}. {item}" for i, item in enumerate(history[-10:])]),
            title="📝 Recent Conversation History",
            border_style="blue"
        ))
    
    def confirm_action(self, message: str) -> bool:
        """Ask for user confirmation."""
        return Confirm.ask(message)
    
    def log_interaction(self, user_input: str, response: str = ""):
        """Log user interaction."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.history.append(f"[{timestamp}] User: {user_input}")
        if response:
            self.history.append(f"[{timestamp}] System: {response}")
