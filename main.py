#!/usr/bin/env python3
"""
Autocoder - AI-Powered Coding Assistant
Terminal-first AI development tool with autonomous capabilities
"""

import sys
from agents.gemini_agent import GeminiAgent
from agents.qwen_agent import QwenAgent
from terminal_interface import TerminalInterface
from core import config, logger
from autonomous_mode import AutonomousAutocoder

def main():
    """Main CLI loop for autocoder with terminal interface."""
    cli = TerminalInterface()
    
    try:
        # Display welcome message
        cli.display_welcome()
        
        # Initialize autonomous autocoder
        cli.display_loading("Initializing AI agents...")
        autocoder = AutonomousAutocoder()
        
        # Display system status
        config_status = config.validate_config()
        cli.display_status(config_status)
        
        cli.display_separator()
        
        while True:
            try:
                user_input = cli.get_user_input()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    cli.display_success("Goodbye! 👋")
                    break
                elif user_input.lower() == 'help':
                    cli.display_help()
                    continue
                elif user_input.lower() == 'status':
                    cli.display_status(config_status)
                    continue
                elif user_input.lower() == 'list':
                    # Get projects from autocoder
                    status = autocoder.get_status()
                    projects = status.get('projects', [])
                    cli.display_projects(projects)
                    continue
                elif user_input.lower() == 'history':
                    cli.display_history(cli.history[-10:])
                    continue
                elif user_input.lower() == 'clear':
                    cli.history.clear()
                    cli.display_success("Conversation history cleared!")
                    continue
                elif user_input.lower().startswith('create '):
                    # Handle project creation
                    description = user_input[7:].strip()
                    if not description:
                        cli.display_error("Please provide a project description.")
                        continue
                    
                    cli.display_loading("Creating project...")
                    result = autocoder.process_request(description)
                    cli.display_project_result(result)
                    cli.log_interaction(user_input, f"Created project: {result.get('project_name', 'Unknown')}")
                    
                elif user_input.lower().startswith('run '):
                    # Handle project execution
                    project_name = user_input[4:].strip()
                    if not project_name:
                        cli.display_error("Please provide a project name.")
                        continue
                    
                    cli.display_loading(f"Running project: {project_name}")
                    # TODO: Implement project execution
                    cli.display_info("Project execution feature coming soon!")
                    
                elif user_input.lower().startswith('debug '):
                    # Handle project debugging
                    project_name = user_input[6:].strip()
                    if not project_name:
                        cli.display_error("Please provide a project name.")
                        continue
                    
                    cli.display_loading(f"Debugging project: {project_name}")
                    # TODO: Implement project debugging
                    cli.display_info("Project debugging feature coming soon!")
                    
                else:
                    # Process general request
                    cli.display_loading("Processing request...")
                    result = autocoder.process_request(user_input)
                    
                    if result.get('success'):
                        cli.display_success("Request processed successfully!")
                        if result.get('project_name'):
                            cli.display_info(f"Created project: {result['project_name']}")
                    else:
                        cli.display_error(f"Request failed: {result.get('error', 'Unknown error')}")
                    
                    cli.log_interaction(user_input, "Request processed")
                    
            except KeyboardInterrupt:
                cli.display_info("Use 'quit' to exit or 'help' for commands.")
                continue
            except Exception as e:
                cli.display_error(f"An error occurred: {str(e)}")
                logger.error(f"Error in main loop: {e}")
                continue
                
    except Exception as e:
        cli.display_error(f"Failed to initialize autocoder: {str(e)}")
        logger.error(f"Initialization error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()