import os
import sys
import subprocess
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import tempfile
import shutil

from core import config, logger

class QwenAgent:
    """Qwen-powered code generation and file operations agent."""
    
    def __init__(self):
        """Initialize Qwen agent with Fireworks AI API integration."""
        self.api_key = config.FIREWORKS_API_KEY
        self.model = config.QWEN_MODEL
        self.base_url = config.FIREWORKS_BASE_URL
        self.max_context_length = config.MAX_CONTEXT_LENGTH
        self.working_directory = os.getcwd()
        
        # API headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Code generation templates
        self.code_templates = {
            "python": {
                "class": "class {name}:\n    def __init__(self):\n        pass\n",
                "function": "def {name}({params}):\n    \"\"\"{docstring}\"\"\"\n    pass\n",
                "script": "#!/usr/bin/env python3\n\"\"\"{description}\"\"\"\n\n{code}\n"
            },
            "javascript": {
                "class": "class {name} {{\n    constructor() {{\n        \n    }}\n}}",
                "function": "function {name}({params}) {{\n    // {docstring}\n}}",
                "module": "// {description}\n\n{code}\n\nexport default {name};"
            }
        }
        
        logger.info("Qwen Agent initialized successfully")

    def execute(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code generation or file operations based on action data."""
        logger.log_agent_action("QWEN", "EXECUTE", f"Action: {action_data.get('action', 'unknown')}")
        
        action_type = action_data.get('action', 'unknown')
        
        try:
            if action_type == 'code_generation':
                return self._generate_code(action_data)
            elif action_type == 'file_operations':
                return self._handle_file_operations(action_data)
            elif action_type == 'cli_operations':
                return self._handle_cli_operations(action_data)
            else:
                return self._handle_conversation_only(action_data)
                
        except Exception as e:
            logger.error(f"Qwen execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "action": action_type
            }

    def _generate_code(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on specifications."""
        try:
            # Extract generation parameters
            language = action_data.get('language', 'python')
            code_type = action_data.get('code_type', 'function')
            name = action_data.get('name', 'generated_code')
            description = action_data.get('description', '')
            requirements = action_data.get('requirements', [])
            
            # Generate code using template or AI
            if self._is_simple_generation(code_type, requirements):
                code = self._generate_from_template(language, code_type, name, description)
            else:
                code = self._generate_with_ai(action_data)
            
            # Create file if specified
            file_path = action_data.get('file_path')
            if file_path:
                self._create_file(file_path, code, language)
                return {
                    "success": True,
                    "action": "code_generation",
                    "file_created": file_path,
                    "code": code,
                    "language": language
                }
            else:
                return {
                    "success": True,
                    "action": "code_generation",
                    "code": code,
                    "language": language
                }
                
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "action": "code_generation"
            }

    def _handle_file_operations(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file creation, modification, and management."""
        try:
            operation = action_data.get('operation', 'create')
            file_path = action_data.get('file_path', '')
            content = action_data.get('content', '')
            
            if operation == 'create':
                self._create_file(file_path, content)
                return {
                    "success": True,
                    "action": "file_operations",
                    "operation": "create",
                    "file_path": file_path
                }
            elif operation == 'modify':
                self._modify_file(file_path, content)
                return {
                    "success": True,
                    "action": "file_operations",
                    "operation": "modify",
                    "file_path": file_path
                }
            elif operation == 'delete':
                self._delete_file(file_path)
                return {
                    "success": True,
                    "action": "file_operations",
                    "operation": "delete",
                    "file_path": file_path
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown file operation: {operation}",
                    "action": "file_operations"
                }
                
        except Exception as e:
            logger.error(f"File operations failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "action": "file_operations"
            }

    def _handle_cli_operations(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle command line operations."""
        try:
            command = action_data.get('command', '')
            working_dir = action_data.get('working_directory', self.working_directory)
            
            if not command:
                return {
                    "success": False,
                    "error": "No command provided",
                    "action": "cli_operations"
                }
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "action": "cli_operations",
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out",
                "action": "cli_operations"
            }
        except Exception as e:
            logger.error(f"CLI operations failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "action": "cli_operations"
            }

    def _handle_conversation_only(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle conversation-only responses."""
        return {
            "success": True,
            "action": "conversation_only",
            "message": "No code generation or file operations needed",
            "response": action_data.get('response', '')
        }

    def _is_simple_generation(self, code_type: str, requirements: List[str]) -> bool:
        """Check if code can be generated from templates."""
        simple_types = ['class', 'function', 'script', 'module']
        return code_type in simple_types and len(requirements) == 0

    def _generate_from_template(self, language: str, code_type: str, name: str, description: str) -> str:
        """Generate code using predefined templates."""
        if language not in self.code_templates:
            language = 'python'
        
        if code_type not in self.code_templates[language]:
            code_type = 'function'
        
        template = self.code_templates[language][code_type]
        
        # Fill template with provided values
        code = template.format(
            name=name,
            params='self' if code_type == 'class' else '',
            docstring=description or f"Generated {code_type}",
            description=description or f"Generated {code_type}",
            code='pass'  # Placeholder
        )
        
        return code

    def _generate_with_ai(self, action_data: Dict[str, Any]) -> str:
        """Generate code using Qwen 3 via Fireworks AI API with Gemini fallback."""
        try:
            language = action_data.get('language', 'python')
            description = action_data.get('description', 'Generated code')
            user_input = action_data.get('user_input', '')
            response = action_data.get('response', '')
            
            # Build prompt for Qwen
            prompt = self._build_qwen_prompt(language, description, user_input, response)
            
            # Call Fireworks AI API
            api_response = self._call_fireworks_api(prompt)
            
            if api_response and 'choices' in api_response:
                generated_code = api_response['choices'][0]['message']['content']
                return self._extract_code_from_response(generated_code, language)
            else:
                logger.warning("Failed to get response from Fireworks AI, trying Gemini fallback")
                return self._generate_with_gemini_fallback(action_data)
                
        except Exception as e:
            logger.warning(f"Fireworks AI code generation failed: {e}, trying Gemini fallback")
            return self._generate_with_gemini_fallback(action_data)
    
    def _generate_with_gemini_fallback(self, action_data: Dict[str, Any]) -> str:
        """Generate code using Gemini as fallback when Fireworks fails."""
        try:
            from agents.gemini_agent import GeminiAgent
            gemini = GeminiAgent()
            
            language = action_data.get('language', 'python')
            description = action_data.get('description', 'Generated code')
            user_input = action_data.get('user_input', '')
            response = action_data.get('response', '')
            
            prompt = f"""Generate {language} code for the following request:

User Request: {user_input}
Description: {description}
Gemini Analysis: {response}

Requirements:
1. Create complete, functional {language} code
2. Include proper error handling and documentation
3. Follow best practices for {language}
4. Make the code modular and maintainable
5. Include necessary imports and dependencies
6. Add helpful comments explaining complex logic

Return only the code, no explanations or markdown formatting. The code should be ready to run."""
            
            generated_code = gemini._generate_gemini_response(prompt)
            return self._extract_code_from_response(generated_code, language)
            
        except Exception as e:
            logger.error(f"Gemini fallback also failed: {e}")
            return self._generate_fallback_code(
                action_data.get('language', 'python'),
                action_data.get('description', 'Generated code')
            )
    
    def _build_qwen_prompt(self, language: str, description: str, user_input: str, gemini_response: str) -> str:
        """Build a comprehensive prompt for Qwen 3."""
        prompt = f"""You are Qwen3-Coder, an expert code generation AI. Generate high-quality, production-ready code based on the following requirements:

Language: {language}
Description: {description}
User Request: {user_input}
Gemini Analysis: {gemini_response}

Instructions:
1. Generate complete, functional code that addresses the user's request
2. Include proper error handling and documentation
3. Follow best practices for {language}
4. Make the code modular and maintainable
5. Include necessary imports and dependencies
6. Add helpful comments explaining complex logic

Generate only the code, no explanations or markdown formatting. The code should be ready to run.

Code:"""
        return prompt
    
    def _call_fireworks_api(self, prompt: str) -> Optional[Dict]:
        """Call Fireworks AI API to generate code."""
        try:
            url = f"{self.base_url}/chat/completions"
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 4000,
                "temperature": 0.1,
                "top_p": 0.9
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Fireworks API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling Fireworks API: {e}")
            return None
    
    def _extract_code_from_response(self, response: str, language: str) -> str:
        """Extract code from Qwen's response, handling various formats."""
        # Remove markdown code blocks if present
        if "```" in response:
            # Find code blocks
            lines = response.split('\n')
            code_lines = []
            in_code_block = False
            
            for line in lines:
                if line.strip().startswith('```'):
                    if in_code_block:
                        break
                    in_code_block = True
                    continue
                if in_code_block:
                    code_lines.append(line)
            
            if code_lines:
                return '\n'.join(code_lines)
        
        # If no code blocks, return the response as-is
        return response.strip()
    
    def _generate_fallback_code(self, language: str, description: str) -> str:
        """Generate fallback code when AI generation fails."""
        if language == 'python':
            return f'''#!/usr/bin/env python3
"""
{description}
Generated by Autocoder (Fallback)
"""

def main():
    """Main function."""
    print("Hello from generated code!")
    # TODO: Implement actual functionality

if __name__ == "__main__":
    main()
'''
        else:
            return f"// {description}\n// Generated by Autocoder (Fallback)\n// TODO: Implement actual functionality\n"

    def _create_file(self, file_path: str, content: str, language: str = 'python') -> None:
        """Create a file with the given content."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Add language-specific headers if needed
        if language == 'python' and not content.startswith('#!/usr/bin/env python3'):
            content = f"#!/usr/bin/env python3\n\"\"\"Generated by Autocoder\"\"\"\n\n{content}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Make executable if it's a script
        if language in ['python', 'bash', 'sh']:
            os.chmod(file_path, 0o755)
        
        logger.info(f"Created file: {file_path}")

    def _modify_file(self, file_path: str, content: str) -> None:
        """Modify an existing file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Modified file: {file_path}")

    def _delete_file(self, file_path: str) -> None:
        """Delete a file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        os.remove(file_path)
        logger.info(f"Deleted file: {file_path}")

    def create_project_structure(self, project_name: str, project_type: str = 'python', description: str = '') -> Dict[str, Any]:
        """Create a complete project structure using AI generation."""
        try:
            project_path = os.path.join(self.working_directory, project_name)
            os.makedirs(project_path, exist_ok=True)
            
            # Generate project structure using AI
            structure = self._generate_project_structure(project_type, project_name, description)
            
            created_files = []
            
            for file_path, file_data in structure.items():
                full_path = os.path.join(project_path, file_path)
                content = file_data.get('content', '')
                language = file_data.get('language', 'python')
                
                self._create_file(full_path, content, language)
                created_files.append(full_path)
            
            # Create README if not already created
            readme_path = os.path.join(project_path, 'README.md')
            if not os.path.exists(readme_path):
                readme_content = self._generate_readme(project_name, project_type, description)
                self._create_file(readme_path, readme_content, 'markdown')
                created_files.append(readme_path)
            
            result = {
                "success": True,
                "project_path": project_path,
                "created_files": created_files,
                "project_type": project_type
            }
            
            # Autonomous mode: Install dependencies and execute if enabled
            if config.AUTONOMOUS_MODE and config.AUTO_INSTALL_DEPS:
                dep_result = self._install_dependencies(project_path, project_type)
                result["dependency_installation"] = dep_result
            
            if config.AUTONOMOUS_MODE and config.AUTO_EXECUTE_PROJECTS:
                exec_result = self._execute_project(project_path, project_type)
                result["execution"] = exec_result
            
            return result
            
        except Exception as e:
            logger.error(f"Project structure creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_project_structure(self, project_type: str, project_name: str, description: str) -> Dict[str, Any]:
        """Generate project structure using AI based on project type."""
        # Define project templates
        templates = {
            'python': {
                'main.py': {
                    'content': f'#!/usr/bin/env python3\n"""Main module for {project_name}."""\n\n\ndef main():\n    """Main function."""\n    print("Hello from {project_name}!")\n\n\nif __name__ == "__main__":\n    main()\n',
                    'language': 'python'
                },
                'requirements.txt': {
                    'content': '# Dependencies for {project_name}\n# Add your dependencies here\n',
                    'language': 'text'
                },
                'setup.py': {
                    'content': f'from setuptools import setup, find_packages\n\nsetup(\n    name="{project_name}",\n    version="0.1.0",\n    description="{description}",\n    packages=find_packages(),\n    python_requires=">=3.8",\n)\n',
                    'language': 'python'
                }
            },
            'javascript': {
                'package.json': {
                    'content': f'{{\n  "name": "{project_name}",\n  "version": "1.0.0",\n  "description": "{description}",\n  "main": "index.js",\n  "scripts": {{\n    "start": "node index.js",\n    "dev": "nodemon index.js"\n  }},\n  "dependencies": {{}}\n}}\n',
                    'language': 'json'
                },
                'index.js': {
                    'content': f'// {project_name}\n// {description}\n\nconsole.log("Hello from {project_name}!");\n',
                    'language': 'javascript'
                }
            },
            'react': {
                'package.json': {
                    'content': f'{{\n  "name": "{project_name}",\n  "version": "0.1.0",\n  "private": true,\n  "dependencies": {{\n    "react": "^18.2.0",\n    "react-dom": "^18.2.0",\n    "react-scripts": "5.0.1"\n  }},\n  "scripts": {{\n    "start": "react-scripts start",\n    "build": "react-scripts build",\n    "test": "react-scripts test",\n    "eject": "react-scripts eject"\n  }}\n}}\n',
                    'language': 'json'
                },
                'src/App.js': {
                    'content': f'import React from \'react\';\nimport \'./App.css\';\n\nfunction App() {{\n  return (\n    <div className="App">\n      <header className="App-header">\n        <h1>{project_name}</h1>\n        <p>{description}</p>\n      </header>\n    </div>\n  );\n}}\n\nexport default App;\n',
                    'language': 'javascript'
                },
                'src/index.js': {
                    'content': 'import React from \'react\';\nimport ReactDOM from \'react-dom/client\';\nimport \'./index.css\';\nimport App from \'./App\';\n\nconst root = ReactDOM.createRoot(document.getElementById(\'root\'));\nroot.render(\n  <React.StrictMode>\n    <App />\n  </React.StrictMode>\n);\n',
                    'language': 'javascript'
                },
                'public/index.html': {
                    'content': f'<!DOCTYPE html>\n<html lang="en">\n  <head>\n    <meta charset="utf-8" />\n    <title>{project_name}</title>\n  </head>\n  <body>\n    <div id="root"></div>\n  </body>\n</html>\n',
                    'language': 'html'
                }
            },
            'fastapi': {
                'main.py': {
                    'content': f'from fastapi import FastAPI\nfrom fastapi.middleware.cors import CORSMiddleware\n\napp = FastAPI(title="{project_name}", description="{description}")\n\napp.add_middleware(\n    CORSMiddleware,\n    allow_origins=["*"],\n    allow_credentials=True,\n    allow_methods=["*"],\n    allow_headers=["*"],\n)\n\n@app.get("/")\nasync def root():\n    return {{"message": "Hello from {project_name}!"}}\n\n@app.get("/health")\nasync def health():\n    return {{"status": "healthy"}}\n\nif __name__ == "__main__":\n    import uvicorn\n    uvicorn.run(app, host="0.0.0.0", port=8000)\n',
                    'language': 'python'
                },
                'requirements.txt': {
                    'content': 'fastapi==0.104.1\nuvicorn[standard]==0.24.0\npydantic==2.5.0\n',
                    'language': 'text'
                }
            }
        }
        
        # Get template for project type, default to python
        structure = templates.get(project_type, templates['python'])
        
        # Use AI to enhance the structure if we have a description
        if description and self.api_key:
            try:
                enhanced_structure = self._enhance_structure_with_ai(project_type, project_name, description, structure)
                return enhanced_structure
            except Exception as e:
                logger.warning(f"Failed to enhance structure with AI: {e}")
                return structure
        
        return structure
    
    def _enhance_structure_with_ai(self, project_type: str, project_name: str, description: str, base_structure: Dict) -> Dict:
        """Enhance project structure using AI based on description."""
        prompt = f"""Generate a complete project structure for a {project_type} project with the following details:

Project Name: {project_name}
Description: {description}
Project Type: {project_type}

Please provide a JSON structure where each key is a file path and each value contains:
- content: The file content
- language: The programming language

Include all necessary files for a production-ready {project_type} project. Make sure to include:
1. Main application files
2. Configuration files
3. Documentation
4. Dependencies
5. Tests if appropriate
6. Any other files needed for the specific project type

Return only valid JSON, no markdown formatting."""
        
        try:
            api_response = self._call_fireworks_api(prompt)
            if api_response and 'choices' in api_response:
                ai_structure = json.loads(api_response['choices'][0]['message']['content'])
                return ai_structure
        except Exception as e:
            logger.warning(f"Fireworks AI structure enhancement failed: {e}")
            # Fallback to Gemini
            try:
                return self._enhance_with_gemini_fallback(project_type, project_name, description, base_structure)
            except Exception as gemini_error:
                logger.warning(f"Gemini fallback also failed: {gemini_error}")
        
        return base_structure
    
    def _enhance_with_gemini_fallback(self, project_type: str, project_name: str, description: str, base_structure: Dict) -> Dict:
        """Fallback to Gemini for project structure enhancement."""
        try:
            from agents.gemini_agent import GeminiAgent
            gemini = GeminiAgent()
            
            prompt = f"""Create a complete {project_type} project structure for: {project_name}
Description: {description}

Generate the main application code that implements the requested functionality. 
Return the code as a Python dictionary where keys are file paths and values are dictionaries with 'content' and 'language' keys.

Example format:
{{
    "main.py": {{
        "content": "#!/usr/bin/env python3\\n\\ndef main():\\n    print('Hello World')\\n\\nif __name__ == '__main__':\\n    main()",
        "language": "python"
    }}
}}

Focus on creating functional, working code that addresses the user's request."""
            
            response = gemini._generate_gemini_response(prompt)
            
            # Try to parse as JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                ai_structure = json.loads(json_match.group())
                return ai_structure
            else:
                # If not JSON, create a simple structure with the response as main.py
                return {
                    "main.py": {
                        "content": response,
                        "language": "python"
                    }
                }
                
        except Exception as e:
            logger.error(f"Gemini fallback failed: {e}")
            return base_structure
    
    def _generate_readme(self, project_name: str, project_type: str, description: str) -> str:
        """Generate a README file for the project."""
        readme = f"""# {project_name}

{description}

## Project Type
{project_type.title()}

## Getting Started

### Prerequisites
- Python 3.8+ (if applicable)
- Node.js (if applicable)
- Other dependencies as listed in requirements.txt or package.json

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd {project_name}

# Install dependencies
"""
        
        if project_type in ['python', 'fastapi']:
            readme += """pip install -r requirements.txt
"""
        elif project_type in ['javascript', 'react']:
            readme += """npm install
"""
        
        readme += f"""
### Running the Project

```bash
"""
        
        if project_type == 'python':
            readme += "python main.py"
        elif project_type == 'fastapi':
            readme += "python main.py\n# or\nuvicorn main:app --reload"
        elif project_type == 'javascript':
            readme += "npm start"
        elif project_type == 'react':
            readme += "npm start"
        
        readme += """
```

## Project Structure

```
{project_name}/
├── README.md
├── main.py (or index.js)
├── requirements.txt (or package.json)
└── ...
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.
"""
        
        return readme
    
    def _install_dependencies(self, project_path: str, project_type: str) -> Dict[str, Any]:
        """Automatically install project dependencies."""
        try:
            logger.info(f"Installing dependencies for {project_type} project at {project_path}")
            
            if project_type in ['python', 'fastapi']:
                # Install Python dependencies
                requirements_file = os.path.join(project_path, 'requirements.txt')
                if os.path.exists(requirements_file):
                    result = subprocess.run(
                        [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    return {
                        "success": result.returncode == 0,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "command": "pip install -r requirements.txt"
                    }
                else:
                    return {"success": True, "message": "No requirements.txt found"}
            
            elif project_type in ['javascript', 'react']:
                # Install Node.js dependencies
                package_json = os.path.join(project_path, 'package.json')
                if os.path.exists(package_json):
                    result = subprocess.run(
                        ['npm', 'install'],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    return {
                        "success": result.returncode == 0,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "command": "npm install"
                    }
                else:
                    return {"success": True, "message": "No package.json found"}
            
            else:
                return {"success": True, "message": f"No dependency installation needed for {project_type}"}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Dependency installation timed out"}
        except Exception as e:
            logger.error(f"Dependency installation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_project(self, project_path: str, project_type: str) -> Dict[str, Any]:
        """Automatically execute the created project."""
        try:
            logger.info(f"Executing {project_type} project at {project_path}")
            
            if project_type == 'python':
                main_file = os.path.join(project_path, 'main.py')
                if os.path.exists(main_file):
                    result = subprocess.run(
                        [sys.executable, 'main.py'],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=config.MAX_EXECUTION_TIME
                    )
                    
                    return {
                        "success": result.returncode == 0,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "command": "python main.py",
                        "return_code": result.returncode
                    }
                else:
                    return {"success": False, "error": "No main.py found"}
            
            elif project_type == 'fastapi':
                main_file = os.path.join(project_path, 'main.py')
                if os.path.exists(main_file):
                    # Try to run with uvicorn
                    result = subprocess.run(
                        [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=config.MAX_EXECUTION_TIME
                    )
                    
                    return {
                        "success": result.returncode == 0,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "command": "uvicorn main:app --host 0.0.0.0 --port 8000",
                        "return_code": result.returncode
                    }
                else:
                    return {"success": False, "error": "No main.py found"}
            
            elif project_type == 'javascript':
                package_json = os.path.join(project_path, 'package.json')
                if os.path.exists(package_json):
                    # Try npm start first, then node index.js
                    commands = [
                        ['npm', 'start'],
                        ['node', 'index.js'],
                        ['node', 'main.js']
                    ]
                    
                    for cmd in commands:
                        try:
                            result = subprocess.run(
                                cmd,
                                cwd=project_path,
                                capture_output=True,
                                text=True,
                                timeout=config.MAX_EXECUTION_TIME
                            )
                            
                            if result.returncode == 0:
                                return {
                                    "success": True,
                                    "stdout": result.stdout,
                                    "stderr": result.stderr,
                                    "command": " ".join(cmd),
                                    "return_code": result.returncode
                                }
                        except subprocess.TimeoutExpired:
                            continue
                    
                    return {"success": False, "error": "All execution attempts failed"}
                else:
                    return {"success": False, "error": "No package.json found"}
            
            elif project_type == 'react':
                package_json = os.path.join(project_path, 'package.json')
                if os.path.exists(package_json):
                    # For React, we'll just verify it can start (don't run indefinitely)
                    result = subprocess.run(
                        ['npm', 'start'],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=30  # Short timeout for React start verification
                    )
                    
                    return {
                        "success": result.returncode == 0,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "command": "npm start",
                        "return_code": result.returncode,
                        "note": "React app started successfully (stopped after 30s)"
                    }
                else:
                    return {"success": False, "error": "No package.json found"}
            
            else:
                return {"success": True, "message": f"No execution needed for {project_type}"}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Project execution timed out after {config.MAX_EXECUTION_TIME}s"}
        except Exception as e:
            logger.error(f"Project execution failed: {e}")
            return {"success": False, "error": str(e)}

    def validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """Validate generated code for syntax errors."""
        try:
            if language == 'python':
                compile(code, '<string>', 'exec')
                return {"valid": True, "errors": []}
            else:
                # For other languages, we'd need specific validators
                return {"valid": True, "errors": [], "note": "Validation not implemented for this language"}
        except SyntaxError as e:
            return {
                "valid": False,
                "errors": [f"Syntax error: {e}"],
                "line": e.lineno
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {e}"]
            }
