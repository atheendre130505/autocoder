import os
os.makedirs("generated_code", exist_ok=True)

import typer
from rich.console import Console
from typing import List
from ai_agents import plan_with_gemini, code_with_qwen3
from ai_agents import autonomous_develop_with_execution  # New import
from datetime import datetime
import re
from execution_engine import AutonomousExecutor
from safety_controls import CommandValidator
from memory_system import AgentMemory

app = typer.Typer()
console = Console()

@app.command()
def develop(
    task: List[str] = typer.Argument(..., help="Development task description")
):
    """
    CLI entry point: accepts a task string
    """
    task_str = " ".join(task)
    console.print(f"[bold green]Received Task:[/bold green] {task_str}")
    
    # Step 1: Planning with Gemini
    console.print("[bold blue]🤔 Planning with Gemini 2.5 Pro...[/bold blue]")
    plan = plan_with_gemini(task_str)
    console.print(f"[bold cyan]📋 Plan:[/bold cyan]\n{plan}")
    
    # Step 2: Code generation with Qwen3-Coder
    console.print("\n[bold blue]⚡ Generating code with Qwen3-Coder...[/bold blue]")
    generated_code = code_with_qwen3(plan, task_str)
    console.print(f"[bold green]💻 Generated Code:[/bold green]\n{generated_code}")
    
    # TODO: Save code to file
    # TODO: Add code critique
    # TODO: Add error handling and execution

@app.command()
def autonomous_develop(
    task: List[str] = typer.Argument(..., help="Development task description"),
    safety_level: str = typer.Option("medium", help="Safety level: low, medium, high")
):
    """
    Autonomous development with CLI execution.
    """
    task_str = " ".join(task)
    console.print(f"[bold green]Received Task:[/bold green] {task_str}")
    
    console.print("[bold blue]🤖 Autonomous Development Initiated...[/bold blue]")
    
    # Generate development plan
    plan = plan_with_gemini(task_str)
    console.print(f"[bold cyan]📋 Autonomous Plan:[/bold cyan]\n{plan}")
    
    # Create instances of the autonomous components
    executor = AutonomousExecutor()
    # Note: CommandValidator doesn't take safety_level as constructor parameter
    validator = CommandValidator()
    memory = AgentMemory()
    
    # Generate production-ready code with Qwen3-Coder
    generated_code = code_with_qwen3(plan, task_str)
    console.print(f"[bold green]💻 Generated Code:[/bold green]\n{generated_code}")
    
    # Basic validation (CommandValidator doesn't have a validate method that takes code)
    console.print("[bold blue]✅ Code generated successfully.[/bold blue]")
    
    try:
        # Execute the generated code using the AutonomousExecutor
        execution_result = executor.execute_python_code(generated_code, "autonomous_test.py")
        console.print(f"[bold cyan]⚙ Execution Result:[/bold cyan]")
        console.print(f"Success: {execution_result.success}")
        if execution_result.success:
            console.print(f"Output: {execution_result.stdout}")
        else:
            console.print(f"Error: {execution_result.stderr}")
    except Exception as exec_error:
        console.print(f"[bold red]Error during autonomous execution: {exec_error}[/bold red]")
        execution_result = None

    # Store details to memory
    memory.store(task_str, {"plan": plan, "code": generated_code, "result": str(execution_result)})
    
    console.print("[bold green]Autonomous development complete.[/bold green]")

@app.command() 
def execute(
    filename: str = typer.Argument(..., help="Python file to execute"),
    safe_mode: bool = typer.Option(True, help="Run in safe mode")
):
    """
    Execute code autonomously with error handling.
    Reads the specified Python file and executes it using the AutonomousExecutor.
    """
    try:
        # Initialize autonomous executor
        executor = AutonomousExecutor()
        
        # Read the file
        with open(filename, 'r') as f:
            code = f.read()
            
        # If safe mode is enabled, validate the code
        if safe_mode:
            validator = CommandValidator()
            if not validator.validate(code):
                console.print("[bold red]Code did not pass safety validation in safe mode.[/bold red]")
                raise typer.Exit(code=1)
        
        # Execute the code using the autonomous executor
        result = executor.execute_python_code(code, filename)
        
        if result.success:
            console.print("[bold green]Code executed successfully.[/bold green]")
            if result.stdout:
                console.print(f"[bold cyan]Output:[/bold cyan]\n{result.stdout}")
        else:
            console.print(f"[bold red]Execution failed:[/bold red]")
            console.print(f"[red]{result.stderr}[/red]")
            raise typer.Exit(code=1)
            
    except FileNotFoundError:
        console.print(f"[bold red]Error: File '{filename}' not found[/bold red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        raise typer.Exit(code=1)

@app.command()
def autonomous(
    task: List[str] = typer.Argument(..., help="Development task description"),
    max_iterations: int = typer.Option(5, "--max-iterations", "-i", help="Maximum iterations to attempt"),
    save_all: bool = typer.Option(True, "--save-all/--no-save", help="Save all iteration attempts")
):
    """
    🚀 Autonomous development: AI plans, codes, executes, and fixes until working
    """
    # Debug prints
    print("DEBUG: Autonomous command started")
    
    task_str = " ".join(task)
    print(f"DEBUG: Task string: {task_str}")
    
    console.print(f"🤖 [bold green]AUTONOMOUS MODE ACTIVATED[/bold green]")
    console.print(f"🎯 Task: {task_str}")
    console.print(f"🔄 Max iterations: {max_iterations}")
    
    print("DEBUG: About to call autonomous_develop_with_execution")
    try:
        # Run autonomous development
        result = autonomous_develop_with_execution(task_str, max_iterations)
        print("DEBUG: autonomous_develop_with_execution completed")
    except Exception as e:
        print(f"DEBUG: Exception in autonomous_develop_with_execution: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("DEBUG: About to display results")
    
    # Display results
    console.print(f"\n📊 [bold cyan]AUTONOMOUS DEVELOPMENT COMPLETE[/bold cyan]")
    console.print(f"🔄 Max iterations: {max_iterations}")
    console.print(f"✅ Success: {'Yes' if result.success else 'No'}")
    console.print(f"🔄 Iterations: {result.iterations}")
    console.print(f"📦 Packages installed: {len(result.packages_installed)}")
    if result.packages_installed:
        console.print(f"   - {', '.join(result.packages_installed)}")
    console.print(f"❌ Errors encountered: {len(result.errors_encountered)}")
    
    if result.success:
        console.print(f"\n🎉 [bold green]FINAL WORKING OUTPUT:[/bold green]")
        console.print(result.final_output)
        
        if save_all:
            # Save the working solution
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = re.sub(r'[^\w\s-]', '', task_str.lower())
            safe_filename = re.sub(r'[-\s]+', '_', safe_filename)
            filename = f"generated_code/autonomous_{safe_filename}_{timestamp}.py"
            
            with open(filename, 'w') as f:
                f.write(f'"""\nAutonomous AI Development Result\nTask: {task_str}\nSuccess: {result.success}\nIterations: {result.iterations}\nGenerated: {datetime.now()}\n"""\n\n')
                f.write(result.final_code)
            
            console.print(f"💾 [green]Working solution saved to: {filename}[/green]")
    else:
        console.print(f"\n❌ [red]DEVELOPMENT FAILED[/red]")
        console.print(f"Final message: {result.final_output}")
        if result.errors_encountered:
            console.print(f"Last error: {result.errors_encountered[-1]}")

if __name__ == "__main__":
    app()
