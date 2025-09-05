import os
from datetime import datetime
from typing import Optional

class PlanManager:
    def __init__(self, plan_file: str = 'planfile.txt'):
        """Initialize the Plan Manager with plan file operations."""
        self.plan_file = plan_file
        if not os.path.exists(self.plan_file):
            self._initialize_plan()
        self.plan_content = ""
        self.load_plan()

    def _initialize_plan(self) -> None:
        """Create initial plan file with project structure."""
        initial_content = """# Plan File for Autocoder

Version: 0.2

## Project Vision
Building a modular AI coding assistant with 8 distinct modules for maintainability and testing.

## Module Breakdown
1. Core Infrastructure & Plan Management ✓
2. Gemini Agent & Research System  
3. Qwen Agent & Code Generation
4. CLI & Terminal Integration
5. Human Approval Workflow
6. Error Detection & Correction
7. IDE Extension Interface
8. Orchestrator & Main Loop

## Development Approach
- Build module by module
- Test each module independently
- Integrate incrementally
- Maintain backwards compatibility

## Current Focus
Module 1: Core Infrastructure & Plan Management - ACTIVE

## Next Steps
1. Create core directory structure ✓
2. Implement plan_manager.py ✓
3. Set up configuration management ✓
4. Test plan file operations
5. Move to Module 2: Gemini Agent integration

## Update Log
- [2025-08-03] Switched to modular architecture approach
- [2025-08-03] Defined 8-module structure with clear responsibilities
- [2025-08-03] Module 1 implementation started
"""
        with open(self.plan_file, 'w', encoding='utf-8') as f:
            f.write(initial_content)

    def load_plan(self) -> bool:
        """Load plan content from file."""
        try:
            with open(self.plan_file, 'r', encoding='utf-8') as f:
                self.plan_content = f.read()
            return True
        except Exception as e:
            print(f"Failed to load plan file: {e}")
            return False

    def save_plan(self) -> bool:
        """Save current plan content to file."""
        try:
            with open(self.plan_file, 'w', encoding='utf-8') as f:
                f.write(self.plan_content)
            return True
        except Exception as e:
            print(f"Failed to save plan file: {e}")
            return False

    def update_plan(self, update_text: str, section: Optional[str] = None) -> None:
        """Update plan with new information and timestamp."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if section:
            # Update specific section
            self._update_section(section, update_text, timestamp)
        else:
            # Add to update log
            update_entry = f"\n## Update [{timestamp}]\n{update_text}\n"
            
            # Find the Update Log section and append
            if "## Update Log" in self.plan_content:
                log_index = self.plan_content.find("## Update Log")
                log_end = len(self.plan_content)
                
                # Insert before the end
                self.plan_content = (
                    self.plan_content[:log_end] + 
                    f"- [{timestamp}] {update_text}\n"
                )
            else:
                # Add new update log section
                self.plan_content += f"\n## Update Log\n- [{timestamp}] {update_text}\n"
        
        self.save_plan()

    def _update_section(self, section: str, content: str, timestamp: str) -> None:
        """Update a specific section of the plan."""
        section_header = f"## {section}"
        if section_header in self.plan_content:
            # Find section boundaries
            start_idx = self.plan_content.find(section_header)
            next_section = self.plan_content.find("\n## ", start_idx + 1)
            
            if next_section == -1:
                # Last section
                self.plan_content = (
                    self.plan_content[:start_idx + len(section_header)] +
                    f"\n{content}\n\n*Updated: {timestamp}*\n"
                )
            else:
                # Middle section
                self.plan_content = (
                    self.plan_content[:start_idx + len(section_header)] +
                    f"\n{content}\n\n*Updated: {timestamp}*\n" +
                    self.plan_content[next_section:]
                )
        else:
            # Add new section
            self.plan_content += f"\n## {section}\n{content}\n\n*Created: {timestamp}*\n"

    def get_plan(self) -> str:
        """Return current plan content."""
        return self.plan_content

    def get_section(self, section: str) -> Optional[str]:
        """Extract specific section from plan."""
        section_header = f"## {section}"
        if section_header in self.plan_content:
            start_idx = self.plan_content.find(section_header)
            next_section = self.plan_content.find("\n## ", start_idx + 1)
            
            if next_section == -1:
                return self.plan_content[start_idx:]
            else:
                return self.plan_content[start_idx:next_section]
        return None

    def mark_module_complete(self, module_number: int, module_name: str) -> None:
        """Mark a module as complete in the plan."""
        self.update_plan(f"Module {module_number}: {module_name} - COMPLETED ✓")
