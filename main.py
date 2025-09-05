from agents.gemini_agent import GeminiAgent
from agents.qwen_agent import QwenAgent
from cli.interface import AutocoderCLI
from core import config, logger
from rich.panel import Panel

def main():
    """Main CLI loop for autocoder with enhanced interface."""
    cli = AutocoderCLI()
    
    try:
        # Display welcome message
        cli.display_welcome()
        
        # Initialize agents
        cli.display_loading("Initializing AI agents...")
        gemini = GeminiAgent()
        qwen = QwenAgent()
        
        # Display system status
        config_status = config.validate_config()
        cli.display_status(config_status, gemini.get_plan_content())
        
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
                elif user_input.lower() == 'plan':
                    cli.console.print(Panel(
                        gemini.get_plan_content(),
                        title="Current Project Plan",
                        border_style="blue"
                    ))
                    continue
                elif user_input.lower() == 'status':
                    cli.display_status(config_status, gemini.get_plan_content())
                    continue
                elif user_input.lower() == 'history':
                    cli.display_history(gemini.get_conversation_context())
                    continue
                elif user_input.lower() == 'clear':
                    gemini.clear_conversation_history()
                    cli.session_history = []
                    cli.display_success("Conversation history cleared")
                    continue
                elif not user_input:
                    continue
                
                # Process user input with Gemini
                cli.display_loading("Gemini is thinking...")
                response = gemini.process_user_input(user_input)
                
                # Display Gemini's response
                cli.display_gemini_response(
                    response['response_to_user'],
                    {
                        'requires_research': response['requires_research'],
                        'research_queries': response['research_queries'],
                        'next_action': response['next_action']
                    }
                )
                
                # Execute action with Qwen if needed
                if response['next_action'] != 'conversation_only':
                    cli.display_loading("Qwen is executing...")
                    
                    # Determine project type and language from user input
                    project_type, language = _detect_project_type(user_input)
                    
                    qwen_result = qwen.execute({
                        'action': response['next_action'],
                        'user_input': user_input,
                        'response': response['response_to_user'],
                        'language': language,
                        'code_type': 'script',
                        'project_type': project_type,
                        'description': _extract_description(user_input)
                    })
                    
                    # Handle project creation specially
                    if 'project' in user_input.lower() and qwen_result.get('success'):
                        project_name = _extract_project_name(user_input)
                        if project_name:
                            project_result = qwen.create_project_structure(
                                project_name, 
                                project_type, 
                                _extract_description(user_input)
                            )
                            if project_result['success']:
                                qwen_result.update(project_result)
                    
                    cli.display_qwen_result(qwen_result)
                
                # Save to session history
                cli.save_session(user_input, response)
                
                cli.display_separator()
                
            except KeyboardInterrupt:
                cli.display_success("\nGoodbye! 👋")
                break
            except Exception as e:
                cli.display_error(f"An error occurred: {e}")
                logger.error(f"Main loop error: {e}")
                
    except Exception as e:
        cli.display_error(f"Failed to initialize autocoder: {e}")
        logger.error(f"Initialization error: {e}")
        cli.display_info("Please check your configuration and try again.")

def _detect_project_type(user_input: str) -> tuple:
    """Detect project type and language from user input."""
    user_lower = user_input.lower()
    
    # Project type detection
    if any(word in user_lower for word in ['react', 'jsx', 'component']):
        return 'react', 'javascript'
    elif any(word in user_lower for word in ['fastapi', 'api', 'rest', 'backend']):
        return 'fastapi', 'python'
    elif any(word in user_lower for word in ['javascript', 'node', 'js']):
        return 'javascript', 'javascript'
    elif any(word in user_lower for word in ['python', 'py', 'django', 'flask']):
        return 'python', 'python'
    else:
        return 'python', 'python'  # Default

def _extract_description(user_input: str) -> str:
    """Extract project description from user input."""
    # Simple extraction - look for descriptive phrases
    words = user_input.split()
    description_words = []
    
    for i, word in enumerate(words):
        if word.lower() in ['for', 'that', 'which', 'to']:
            description_words = words[i+1:]
            break
    
    if not description_words:
        description_words = words[2:]  # Skip first two words (usually "create a")
    
    return ' '.join(description_words) if description_words else 'Generated project'

def _extract_project_name(user_input: str) -> str:
    """Extract project name from user input."""
    import re
    
    # Look for patterns like "create a project called X" or "create X project"
    patterns = [
        r'create\s+(?:a\s+)?(?:project\s+)?(?:called\s+)?(\w+)',
        r'build\s+(?:a\s+)?(?:project\s+)?(?:called\s+)?(\w+)',
        r'make\s+(?:a\s+)?(?:project\s+)?(?:called\s+)?(\w+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, user_input.lower())
        if match:
            return match.group(1)
    
    # Fallback - use first word after "create"
    words = user_input.lower().split()
    if 'create' in words:
        idx = words.index('create')
        if idx + 1 < len(words):
            return words[idx + 1]
    
    return 'autocoder_project'

if __name__ == "__main__":
    main()
