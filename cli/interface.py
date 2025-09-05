"""
Enhanced CLI interface for autocoder with rich formatting and better UX.
"""

import os
import sys
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.markdown import Markdown

class AutocoderCLI:
    """Enhanced CLI interface with rich formatting."""
    
    def __init__(self):
        self.console = Console()
        self.session_history = []
        self.current_project = None
        
    def display_welcome(self):
        """Display welcome message and project info."""
        welcome_text = """
# 🚀 Autocoder - AI-Powered Coding Assistant

Welcome to Autocoder! Your intelligent coding companion that combines:
- **Gemini 2.0** for research, planning, and problem diagnosis
- **Qwen Coder** for code generation and file operations
- **GitHub & Stack Overflow** integration for research

Type `help` for commands or start asking questions!
        """
        
        self.console.print(Panel(
            Markdown(welcome_text),
            title="Welcome",
            border_style="blue"
        ))
    
    def display_help(self):
        """Display comprehensive help information."""
        help_table = Table(title="Available Commands", show_header=True, header_style="bold magenta")
        help_table.add_column("Command", style="cyan", no_wrap=True)
        help_table.add_column("Description", style="white")
        
        commands = [
            ("help", "Show this help message"),
            ("plan", "Display current project plan"),
            ("status", "Show system status and configuration"),
            ("history", "Show recent conversation history"),
            ("clear", "Clear conversation history"),
            ("quit/exit/q", "Exit the program"),
            ("", ""),
            ("", "**Usage Examples:**"),
            ("", ""),
            ("Create a Python CLI tool", "Generate a command-line application"),
            ("Find GitHub projects for...", "Research similar repositories"),
            ("Build a REST API with FastAPI", "Generate API code and structure"),
            ("Create a React component", "Generate React component code"),
            ("Debug this error: ...", "Analyze and fix code issues"),
            ("Set up project structure", "Create complete project layout")
        ]
        
        for command, description in commands:
            help_table.add_row(command, description)
        
        self.console.print(help_table)
    
    def display_status(self, config_status: Dict[str, bool], plan_content: str):
        """Display system status and configuration."""
        status_table = Table(title="System Status", show_header=True, header_style="bold green")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="white")
        
        # API Status
        status_table.add_row("Gemini API", "✅ Connected" if config_status.get('gemini_key_present') else "❌ Not configured")
        status_table.add_row("GitHub API", "✅ Connected" if config_status.get('github_token_present') else "⚠️  Optional")
        status_table.add_row("Project Root", "✅ Valid" if config_status.get('project_root_exists') else "❌ Invalid")
        status_table.add_row("Plan File", "✅ Writable" if config_status.get('plan_file_writable') else "❌ Read-only")
        
        self.console.print(status_table)
        
        # Plan preview
        if plan_content:
            plan_preview = plan_content[:200] + "..." if len(plan_content) > 200 else plan_content
            self.console.print(Panel(
                plan_preview,
                title="Current Plan Preview",
                border_style="yellow"
            ))
    
    def display_history(self, history: list, limit: int = 10):
        """Display conversation history."""
        if not history:
            self.console.print("[yellow]No conversation history available.[/yellow]")
            return
        
        history_table = Table(title=f"Recent Conversation History (Last {min(limit, len(history))} messages)", show_header=True)
        history_table.add_column("Time", style="dim", width=12)
        history_table.add_column("Role", style="bold", width=8)
        history_table.add_column("Message", style="white")
        
        for msg in history[-limit:]:
            timestamp = msg.get('timestamp', 'Unknown')[:16]  # Truncate timestamp
            role = msg.get('role', 'unknown').title()
            content = msg.get('content', '')[:100] + "..." if len(msg.get('content', '')) > 100 else msg.get('content', '')
            
            history_table.add_row(timestamp, role, content)
        
        self.console.print(history_table)
    
    def display_gemini_response(self, response: str, research_info: Optional[Dict] = None):
        """Display Gemini's response with formatting."""
        # Main response
        self.console.print(Panel(
            response,
            title="🤖 Gemini Response",
            border_style="blue"
        ))
        
        # Research information if available
        if research_info and research_info.get('requires_research'):
            research_text = f"🔍 Research conducted:\n"
            if research_info.get('research_queries'):
                research_text += f"Queries: {', '.join(research_info['research_queries'])}\n"
            research_text += f"Next action: {research_info.get('next_action', 'conversation_only')}"
            
            self.console.print(Panel(
                research_text,
                title="Research Summary",
                border_style="green"
            ))
    
    def display_qwen_result(self, result: Dict[str, Any]):
        """Display Qwen's execution result."""
        if result.get('success'):
            success_text = f"✅ {result.get('message', 'Action completed successfully')}"
            
            # Add file information if available
            if 'file_created' in result:
                success_text += f"\n📁 File created: {result['file_created']}"
            if 'project_path' in result:
                success_text += f"\n📁 Project created: {result['project_path']}"
            if 'created_files' in result:
                success_text += f"\n📁 Files created: {len(result['created_files'])}"
            
            self.console.print(Panel(
                success_text,
                title="🔧 Qwen Execution",
                border_style="green"
            ))
            
            # Show generated code if available
            if 'code' in result and result['code']:
                try:
                    syntax = Syntax(result['code'], result.get('language', 'python'), theme="monokai")
                    self.console.print(Panel(
                        syntax,
                        title="Generated Code",
                        border_style="yellow"
                    ))
                except Exception:
                    # Fallback to plain text if syntax highlighting fails
                    self.console.print(Panel(
                        result['code'],
                        title="Generated Code",
                        border_style="yellow"
                    ))
        else:
            error_text = f"❌ Error: {result.get('error', 'Unknown error occurred')}"
            self.console.print(Panel(
                error_text,
                title="🔧 Qwen Execution Failed",
                border_style="red"
            ))
    
    def get_user_input(self, prompt: str = "> ") -> str:
        """Get user input with enhanced prompt."""
        return Prompt.ask(prompt, console=self.console)
    
    def confirm_action(self, message: str) -> bool:
        """Ask for user confirmation."""
        return Confirm.ask(message, console=self.console)
    
    def display_error(self, error: str, details: Optional[str] = None):
        """Display error message with formatting."""
        error_text = f"❌ {error}"
        if details:
            error_text += f"\n\nDetails: {details}"
        
        self.console.print(Panel(
            error_text,
            title="Error",
            border_style="red"
        ))
    
    def display_success(self, message: str):
        """Display success message."""
        self.console.print(f"[green]✅ {message}[/green]")
    
    def display_warning(self, message: str):
        """Display warning message."""
        self.console.print(f"[yellow]⚠️  {message}[/yellow]")
    
    def display_info(self, message: str):
        """Display info message."""
        self.console.print(f"[blue]ℹ️  {message}[/blue]")
    
    def display_separator(self):
        """Display a visual separator."""
        self.console.print("─" * 60)
    
    def display_loading(self, message: str = "Processing..."):
        """Display loading indicator."""
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[blue]{message}[/blue]"),
            console=self.console,
            transient=True
        ) as progress:
            progress.add_task("processing", total=None)
    
    def clear_screen(self):
        """Clear the console screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def save_session(self, user_input: str, response: Dict[str, Any]):
        """Save interaction to session history."""
        self.session_history.append({
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'user_input': user_input,
            'response': response
        })
        
        # Keep only last 50 interactions
        if len(self.session_history) > 50:
            self.session_history = self.session_history[-50:]
    
    def get_session_history(self) -> list:
        """Get session history for context."""
        return self.session_history[-10:]  # Last 10 interactions
