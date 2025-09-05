#!/usr/bin/env python3
"""
Autonomous Mode for Autocoder
Runs projects without human intervention - fully automated.
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, Any, List

from agents.gemini_agent import GeminiAgent
from agents.qwen_agent import QwenAgent
from core import config, logger

class AutonomousAutocoder:
    """Fully autonomous autocoder that creates and executes projects without human intervention."""
    
    def __init__(self):
        """Initialize autonomous autocoder."""
        self.gemini = GeminiAgent('autonomous_plan.txt')
        self.qwen = QwenAgent()
        self.projects_created = []
        self.execution_results = []
        
        logger.info("Autonomous Autocoder initialized")
    
    def process_request(self, request: str) -> Dict[str, Any]:
        """Process a request and create/execute project autonomously."""
        logger.info(f"Processing autonomous request: {request}")
        
        try:
            # Step 1: Gemini analyzes the request
            gemini_response = self.gemini.process_user_input(request)
            
            # Step 2: Determine project details
            project_type, language = self._detect_project_type(request)
            project_name = self._extract_project_name(request)
            description = self._extract_description(request)
            
            # Step 3: Create project structure
            logger.info(f"Creating {project_type} project: {project_name}")
            project_result = self.qwen.create_project_structure(
                project_name, 
                project_type, 
                request  # Pass the full user request as description for AI enhancement
            )
            
            if not project_result['success']:
                return {
                    "success": False,
                    "error": f"Project creation failed: {project_result.get('error', 'Unknown error')}",
                    "request": request
                }
            
            # Step 4: Record project creation
            self.projects_created.append({
                "name": project_name,
                "type": project_type,
                "path": project_result['project_path'],
                "files": project_result['created_files'],
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 5: Handle dependencies and execution
            execution_info = {}
            
            if 'dependency_installation' in project_result:
                dep_result = project_result['dependency_installation']
                execution_info['dependencies'] = {
                    "success": dep_result['success'],
                    "command": dep_result.get('command', ''),
                    "message": dep_result.get('message', dep_result.get('error', ''))
                }
            
            if 'execution' in project_result:
                exec_result = project_result['execution']
                execution_info['execution'] = {
                    "success": exec_result['success'],
                    "command": exec_result.get('command', ''),
                    "stdout": exec_result.get('stdout', ''),
                    "stderr": exec_result.get('stderr', ''),
                    "return_code": exec_result.get('return_code', 0)
                }
                
                # Record execution result
                self.execution_results.append({
                    "project": project_name,
                    "success": exec_result['success'],
                    "timestamp": datetime.now().isoformat(),
                    "details": exec_result
                })
            
            # Step 6: Generate summary
            summary = self._generate_summary(project_result, execution_info)
            
            return {
                "success": True,
                "project_name": project_name,
                "project_type": project_type,
                "project_path": project_result['project_path'],
                "created_files": project_result['created_files'],
                "execution_info": execution_info,
                "summary": summary,
                "gemini_analysis": gemini_response['response_to_user']
            }
            
        except Exception as e:
            logger.error(f"Autonomous processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "request": request
            }
    
    def _detect_project_type(self, request: str) -> tuple:
        """Detect project type and language from request."""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ['react', 'jsx', 'component', 'frontend']):
            return 'react', 'javascript'
        elif any(word in request_lower for word in ['fastapi', 'api', 'rest', 'backend', 'server']):
            return 'fastapi', 'python'
        elif any(word in request_lower for word in ['javascript', 'node', 'js', 'express']):
            return 'javascript', 'javascript'
        elif any(word in request_lower for word in ['python', 'py', 'django', 'flask', 'script']):
            return 'python', 'python'
        else:
            return 'python', 'python'  # Default
    
    def _extract_project_name(self, request: str) -> str:
        """Extract project name from request."""
        import re
        import time
        
        patterns = [
            r'create\s+(?:a\s+)?(?:project\s+)?(?:called\s+)?(\w+)',
            r'build\s+(?:a\s+)?(?:project\s+)?(?:called\s+)?(\w+)',
            r'make\s+(?:a\s+)?(?:project\s+)?(?:called\s+)?(\w+)',
            r'generate\s+(?:a\s+)?(?:project\s+)?(?:called\s+)?(\w+)',
            r'(\w+)\s+(?:project|app|program|script|tool)',
            r'(\w+)\s+(?:manager|calculator|scraper|generator)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, request.lower())
            if match:
                name = match.group(1)
                if name not in ['python', 'javascript', 'web', 'app', 'program']:
                    return name
        
        # Fallback: use timestamp-based name
        return f"project_{int(time.time())}"
    
    def _extract_description(self, request: str) -> str:
        """Extract project description from request."""
        words = request.split()
        description_words = []
        
        for i, word in enumerate(words):
            if word.lower() in ['for', 'that', 'which', 'to', 'with']:
                description_words = words[i+1:]
                break
        
        if not description_words:
            description_words = words[2:]  # Skip first two words
        
        return ' '.join(description_words) if description_words else 'Autonomous project'
    
    def _generate_summary(self, project_result: Dict, execution_info: Dict) -> str:
        """Generate a summary of the autonomous execution."""
        summary = f"✅ Project created successfully!\n"
        summary += f"📁 Project: {project_result['project_path']}\n"
        summary += f"📄 Files created: {len(project_result['created_files'])}\n"
        
        if 'dependencies' in execution_info:
            dep_info = execution_info['dependencies']
            if dep_info['success']:
                summary += f"📦 Dependencies: Installed successfully\n"
            else:
                summary += f"⚠️  Dependencies: {dep_info['message']}\n"
        
        if 'execution' in execution_info:
            exec_info = execution_info['execution']
            if exec_info['success']:
                summary += f"🚀 Execution: Successful\n"
                if exec_info['stdout']:
                    summary += f"📤 Output: {exec_info['stdout'][:200]}...\n"
            else:
                summary += f"❌ Execution: Failed - {exec_info.get('stderr', 'Unknown error')}\n"
        
        return summary
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of autonomous operations."""
        return {
            "projects_created": len(self.projects_created),
            "successful_executions": len([r for r in self.execution_results if r['success']]),
            "failed_executions": len([r for r in self.execution_results if not r['success']]),
            "projects": self.projects_created,
            "execution_results": self.execution_results
        }
    
    def save_report(self, filename: str = None) -> str:
        """Save a detailed report of all operations."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"autonomous_report_{timestamp}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "status": self.get_status(),
            "config": {
                "autonomous_mode": config.AUTONOMOUS_MODE,
                "auto_install_deps": config.AUTO_INSTALL_DEPS,
                "auto_execute_projects": config.AUTO_EXECUTE_PROJECTS,
                "max_execution_time": config.MAX_EXECUTION_TIME
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Autonomous report saved to {filename}")
        return filename

def main():
    """Main autonomous mode function."""
    print("🤖 Autonomous Autocoder - Fully Automated Mode")
    print("=" * 50)
    
    # Check configuration
    if not config.AUTONOMOUS_MODE:
        print("❌ Autonomous mode is disabled in configuration")
        print("Set AUTONOMOUS_MODE=true in .env file")
        return
    
    autocoder = AutonomousAutocoder()
    
    # Example requests to process
    example_requests = [
        "Create a Python calculator with basic arithmetic operations",
        "Build a simple FastAPI REST API for a todo list",
        "Create a React component for a user profile card",
        "Make a JavaScript CLI tool for file management"
    ]
    
    print(f"🚀 Processing {len(example_requests)} example requests...")
    print()
    
    for i, request in enumerate(example_requests, 1):
        print(f"📋 Request {i}: {request}")
        print("-" * 40)
        
        result = autocoder.process_request(request)
        
        if result['success']:
            print(f"✅ Success: {result['project_name']}")
            print(f"📁 Location: {result['project_path']}")
            print(f"📄 Files: {len(result['created_files'])}")
            
            if 'execution_info' in result:
                exec_info = result['execution_info']
                if 'execution' in exec_info:
                    exec_result = exec_info['execution']
                    if exec_result['success']:
                        print(f"🚀 Execution: Successful")
                        if exec_result['stdout']:
                            print(f"📤 Output: {exec_result['stdout'][:100]}...")
                    else:
                        print(f"❌ Execution: Failed")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        
        print()
        time.sleep(1)  # Brief pause between requests
    
    # Generate final report
    print("📊 Generating final report...")
    report_file = autocoder.save_report()
    print(f"📄 Report saved to: {report_file}")
    
    # Show final status
    status = autocoder.get_status()
    print(f"\n🎯 Final Status:")
    print(f"   Projects created: {status['projects_created']}")
    print(f"   Successful executions: {status['successful_executions']}")
    print(f"   Failed executions: {status['failed_executions']}")

if __name__ == "__main__":
    main()
