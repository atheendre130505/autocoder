# ai_agents.py
import requests
import os
import json
import time
from rich.console import Console
from typing import Dict, List, Optional
from dataclasses import dataclass
from config import get_config

# Import our new autonomous capabilities
from execution_engine import AutonomousExecutor, ExecutionResult
from safety_controls import validate_command, CommandValidator
from error_analyzer import ErrorAnalyzer

console = Console()

@dataclass
class AutonomousResult:
    """Result of autonomous development process"""
    success: bool
    final_code: str
    execution_results: List[ExecutionResult]
    iterations: int
    final_output: str
    errors_encountered: List[str]
    packages_installed: List[str]

class AutonomousAgent:
    """Base class for autonomous AI agents with execution capabilities"""
    
    def __init__(self, model_name: str, role: str, executor: AutonomousExecutor):
        self.model = model_name
        self.role = role
        self.executor = executor
        self.error_analyzer = ErrorAnalyzer(self)
        
        console.print(f"🤖 [bold blue]{self.role} agent[/bold blue] initialized with autonomous capabilities")

    def autonomous_develop(self, task: str) -> dict:
        """
        Generate a development plan using Gemini, produce production-ready code via Qwen3-Coder,
        execute it autonomously, and return a summary of the process.
        """
        # Generate the development plan
        plan = plan_with_gemini(task)
        console.print(f"[bold cyan]📋 Autonomous Plan:[/bold cyan]\n{plan}")
        # Generate code, validate, execute, and analyze
        code_exec_result = autonomous_code_with_qwen3(plan, task, self.executor)
        return {
            "plan": plan,
            "generated_code": code_exec_result.get("generated_code"),
            "execution_result": code_exec_result.get("execution_result"),
            "analysis": code_exec_result.get("analysis")
        }

# Existing planning function
def plan_with_gemini(task_description: str) -> str:
    """
    Uses Gemini 2.5 Pro to create a development plan
    """
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        return "Error: GEMINI_API_KEY not found in environment variables"
    
    headers = {"Content-Type": "application/json"}
    
    prompt = f"""You are a software development planning agent. Create a detailed, step-by-step plan for the following task:

Task: {task_description}

Please provide:
1. A clear breakdown of what needs to be built
2. Step-by-step implementation approach
3. Key considerations and potential challenges
4. Suggested file structure or components

Keep your response focused and actionable."""
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(
            f"{api_url}?key={api_key}",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error: Gemini API returned status {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"

def clean_generated_code(code: str) -> str:
    """
    Clean up generated code to remove non-Python content
    """
    lines = code.split('\n')
    cleaned_lines = []
    in_code_block = False
    
    for line in lines:
        # Skip markdown code block markers
        if line.strip().startswith('```'):  # FIXED: Properly closed string
            in_code_block = not in_code_block
            continue
            
        # Skip lines that look like natural language explanations
        stripped = line.strip()
        if (stripped.startswith("I'll") or 
            stripped.startswith("This") or 
            stripped.startswith("Here") or
            stripped.startswith("The following") or
            stripped.startswith("Let me") or
            stripped.startswith("Now I'll") or
            stripped.startswith("First,") or
            stripped.startswith("Next,") or
            (stripped and not any(c in stripped for c in ['=', '(', ')', ':', 'import', 'def', 'class', 'if', 'for', 'while', 'try', 'print', '#']))):
            continue
            
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines).strip()


# IMPROVED CODE GENERATION FUNCTION
def code_with_qwen3(plan: str, task: str) -> str:
    """
    Uses Qwen3-Coder to generate code based on the plan
    """
    api_url = "https://api.fireworks.ai/inference/v1/chat/completions"
    api_key = os.getenv('FIREWORKS_API_KEY')
    
    if not api_key:
        return "Error: FIREWORKS_API_KEY not found in environment variables"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # IMPROVED PROMPT - More explicit about code-only output
    prompt = f"""Generate ONLY executable Python code for the following task. Do not include any explanations, comments about what you'll do, or natural language descriptions.

TASK: {task}

PLAN: {plan}

Requirements:
- Generate ONLY Python code that can be executed directly
- Include proper error handling
- Add necessary imports
- Include a main section that demonstrates the functionality
- NO explanations or natural language - just pure Python code
- Start immediately with Python code (imports, functions, etc.)

Generate the complete, runnable Python code now:"""

    payload = {
        "model": "accounts/fireworks/models/qwen3-coder-480b-a35b-instruct",
        "messages": [
            {"role": "system", "content": "You are a Python code generator. Output only executable Python code with no explanations or natural language. Start immediately with Python code."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4000,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            # ADD DEBUG OUTPUT
            print(f"🔍 DEBUG: API Response keys: {result.keys()}")
            print(f"🔍 DEBUG: Full response: {json.dumps(result, indent=2)[:500]}...")
            
            # Check if 'choices' exists and what type it is
            if 'choices' in result:
                print(f"🔍 DEBUG: choices type: {type(result['choices'])}")
                print(f"🔍 DEBUG: choices content: {result['choices']}")
            
            # FIXED: Safer response parsing
            if 'choices' in result and len(result['choices']) > 0:
                if 'message' in result['choices']:
                    generated_code = result['choices']['message']['content']
                elif 'text' in result['choices']:
                    generated_code = result['choices']['text']
                else:
                    generated_code = str(result['choices'])
            else:
                return f"Error: Unexpected API response structure: {result}"
            
            # ADDED: Clean up the generated code
            return clean_generated_code(generated_code)
        else:
            return f"Error: Fireworks API returned status {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error calling Qwen3-Coder API: {str(e)}"

# Enhanced autonomous function with execution capabilities
def autonomous_code_with_qwen3(plan: str, task: str, executor: AutonomousExecutor) -> dict:
    """
    Enhanced version of code_with_qwen3 with execution capabilities.
    Generates code and executes it directly, with simplified error handling.
    """
    api_url = "https://api.fireworks.ai/inference/v1/chat/completions"
    api_key = os.getenv('FIREWORKS_API_KEY')
    
    if not api_key:
        return {"error": "Error: FIREWORKS_API_KEY not found in environment variables"}
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # Use the same improved prompt as code_with_qwen3
    prompt = f"""Generate ONLY executable Python code for the following task. Do not include any explanations, comments about what you'll do, or natural language descriptions.

TASK: {task}

PLAN: {plan}

Requirements:
- Generate ONLY Python code that can be executed directly
- Include proper error handling
- Add necessary imports
- Include a main section that demonstrates the functionality
- NO explanations or natural language - just pure Python code
- Start immediately with Python code (imports, functions, etc.)

Generate the complete, runnable Python code now:"""
    
    payload = {
        "model": "accounts/fireworks/models/qwen3-coder-480b-a35b-instruct",
        "messages": [
            {"role": "system", "content": "You are a Python code generator. Output only executable Python code with no explanations or natural language. Start immediately with Python code."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4000,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            
            # FIXED: Use same safer parsing as code_with_qwen3
            if 'choices' in result and len(result['choices']) > 0:
                if 'message' in result['choices']:
                    generated_code = result['choices']['message']['content']
                elif 'text' in result['choices']:
                    generated_code = result['choices']['text']
                else:
                    generated_code = str(result['choices'])
            else:
                return {"error": f"Unexpected API response structure: {result}"}
                
            # Clean the generated code
            generated_code = clean_generated_code(generated_code)
        else:
            return {"error": f"Error: Fireworks API returned status {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": f"Error calling Qwen3-Coder API: {str(e)}"}
    
    # Execute the code directly using the provided executor
    try:
        execution_result = executor.execute_python_code(
            generated_code, 
            f"autonomous_code_{int(time.time())}.py"
        )
    except Exception as exec_error:
        execution_result = ExecutionResult(
            command="",
            stdout="",
            stderr=str(exec_error),
            exit_code=-1,
            execution_time=0.0,
            success=False
        )
    
    # Simplified analysis - just return the results
    analysis = {
        "error_type": execution_result.error_type if hasattr(execution_result, 'error_type') and not execution_result.success else None,
        "execution_time": execution_result.execution_time if hasattr(execution_result, 'execution_time') else 0.0
    }
    
    return {
        "generated_code": generated_code,
        "execution_result": execution_result,
        "analysis": analysis
    }

def extract_missing_packages(error_message: str) -> List[str]:
    """Extract missing package names from error messages"""
    import re
    packages = []
    
    # Common patterns for missing modules
    patterns = [
        r"No module named '([^']+)'",
        r"ModuleNotFoundError: No module named '([^']+)'",
        r"ImportError: No module named ([^\s]+)",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, error_message)
        packages.extend(matches)
    
    return list(set(packages))

def critique_code(code: str, task: str) -> str:
    """
    Uses Qwen3-Coder to critique and review generated code.
    """
    api_url = "https://api.fireworks.ai/inference/v1/chat/completions"
    api_key = os.getenv('FIREWORKS_API_KEY')
    
    if not api_key:
        return "Error: FIREWORKS_API_KEY not found in environment variables"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    prompt = f"""You are an expert code reviewer. Please review the following code and provide:

ORIGINAL TASK: {task}

CODE TO REVIEW:
{code}

Please provide:
1. **Code Quality Assessment**: Overall quality, readability, maintainability
2. **Bug Analysis**: Potential bugs, edge cases not handled
3. **Performance Review**: Efficiency, optimization opportunities
4. **Best Practices**: Adherence to coding standards and best practices
5. **Security Considerations**: Any security issues or vulnerabilities
6. **Improvement Suggestions**: Specific recommendations for enhancement
7. **Test Coverage**: What tests should be added

Be thorough but constructive in your feedback."""
    
    payload = {
        "model": "accounts/fireworks/models/qwen3-coder-480b-a35b-instruct",
        "messages": [
            {"role": "system", "content": "You are a senior software engineer and code reviewer with expertise in best practices, security, and performance optimization."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 3000,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            # Use safer parsing here too
            if 'choices' in result and len(result['choices']) > 0:
                if 'message' in result['choices']:
                    return result['choices']['message']['content']
                elif 'text' in result['choices']:
                    return result['choices']['text']
                else:
                    return str(result['choices'])
            else:
                return f"Error: Unexpected API response structure: {result}"
        else:
            return f"Error: Fireworks API returned status {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error calling code critique API: {str(e)}"

# NEW: Define autonomous_develop_with_execution so it can be imported by main.py
def autonomous_develop_with_execution(task: str, max_iterations: int = 5) -> AutonomousResult:
    """
    Autonomous development cycle: Plan -> Code -> Execute -> Fix -> Repeat until working
    """
    console.print(f"🚀 [bold green]Starting autonomous development for:[/bold green] {task}")
    
    # Initialize autonomous agent (FIXED: correct constructor)
    executor = AutonomousExecutor()
    agent = AutonomousAgent("qwen3-coder", "autonomous_developer", executor)
    
    # Step 1: Create initial plan
    console.print("🤔 [bold blue]Planning with Gemini...[/bold blue]")
    plan = plan_with_gemini(task)
    console.print(f"📋 Plan created: {len(plan)} characters")
    
    execution_results = []
    errors_encountered = []
    packages_installed = []
    generated_code = ""
    
    for iteration in range(max_iterations):
        console.print(f"\n🔄 [bold yellow]Iteration {iteration + 1}/{max_iterations}[/bold yellow]")
        
        # Step 2: Generate code
        console.print("⚡ [bold blue]Generating code with Qwen3-Coder...[/bold blue]")
        if iteration == 0:
            generated_code = code_with_qwen3(plan, task)
        else:
            error_context = f"\n\nPREVIOUS ERRORS TO FIX:\n{chr(10).join(errors_encountered[-3:])}"
            generated_code = code_with_qwen3(plan + error_context, task)
        
        if generated_code.startswith("Error:"):
            console.print(f"❌ [red]Code generation failed: {generated_code}[/red]")
            return AutonomousResult(
                success=False,
                final_code=generated_code,
                execution_results=execution_results,
                iterations=iteration + 1,
                final_output="Code generation failed",
                errors_encountered=errors_encountered,
                packages_installed=packages_installed
            )
        
        # Step 3: Execute the generated code
        console.print("🔧 [bold blue]Executing generated code...[/bold blue]")
        filename = f"autonomous_iteration_{iteration + 1}.py"
        exec_result = executor.execute_python_code(generated_code, filename)
        execution_results.append(exec_result)
        
        if exec_result.success:
            console.print("✅ [bold green]Code executed successfully![/bold green]")
            console.print(f"📤 Output:\n{exec_result.stdout}")
            
            return AutonomousResult(
                success=True,
                final_code=generated_code,
                execution_results=execution_results,
                iterations=iteration + 1,
                final_output=exec_result.stdout,
                errors_encountered=errors_encountered,
                packages_installed=packages_installed
            )
        else:
            # Step 4: Handle errors
            console.print(f"❌ [red]Execution failed:[/red] {exec_result.stderr}")
            errors_encountered.append(exec_result.stderr)
            
            # Try to auto-fix missing dependencies
            if exec_result.error_type == "MISSING_MODULE":
                missing_packages = extract_missing_packages(exec_result.stderr)
                for package in missing_packages:
                    console.print(f"📦 [yellow]Auto-installing missing package: {package}[/yellow]")
                    install_result = executor.install_package(package)
                    if install_result.success:
                        packages_installed.append(package)
                        console.print(f"✅ [green]Package {package} installed successfully[/green]")
                        
                        # Retry execution after installing package
                        console.print("🔄 [blue]Retrying execution after package installation...[/blue]")
                        retry_result = executor.execute_python_code(generated_code, f"{filename}_retry")
                        execution_results.append(retry_result)
                        
                        if retry_result.success:
                            console.print("✅ [bold green]Code executed successfully after package installation![/bold green]")
                            return AutonomousResult(
                                success=True,
                                final_code=generated_code,
                                execution_results=execution_results,
                                iterations=iteration + 1,
                                final_output=retry_result.stdout,
                                errors_encountered=errors_encountered,
                                packages_installed=packages_installed
                            )
    
    # Max iterations reached without success
    console.print(f"❌ [red]Failed to create working solution after {max_iterations} iterations[/red]")
    return AutonomousResult(
        success=False,
        final_code=generated_code if 'generated_code' in locals() else "No code generated",
        execution_results=execution_results,
        iterations=max_iterations,
        final_output="Max iterations reached without success",
        errors_encountered=errors_encountered,
        packages_installed=packages_installed
    )
