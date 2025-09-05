import os
import google.generativeai as genai
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import re

from core import PlanManager, config, logger
from research.github_search import GitHubSearcher
from research.stackoverflow_search import StackOverflowSearcher

class GeminiAgent:
    """Gemini-powered conversational agent with research capabilities."""
    
    def __init__(self, plan_file: str = 'planfile.txt'):
        """Initialize Gemini agent with plan management and research tools."""
        self.plan_manager = PlanManager(plan_file)
        self.github_searcher = GitHubSearcher()
        self.so_searcher = StackOverflowSearcher()
        
        # Initialize Gemini
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        
        # Conversation memory
        self.conversation_history = []
        self.research_cache = {}
        
        logger.info("Gemini Agent initialized successfully")

    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input and determine next actions."""
        logger.log_agent_action("GEMINI", "PROCESS_INPUT", f"User: {user_input[:100]}...")
        
        # Add to conversation history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "user",
            "content": user_input
        })
        
        # Analyze input for research needs
        research_needed = self._analyze_research_needs(user_input)
        
        response = {
            "requires_research": research_needed,
            "research_queries": [],
            "next_action": "",
            "plan_updates": [],
            "response_to_user": ""
        }
        
        # Perform research if needed
        if research_needed:
            research_results = self._conduct_research(user_input)
            response["research_queries"] = research_results.get("queries", [])
            
            # Update plan with research findings
            self._update_plan_with_research(research_results)
        
        # Generate response using Gemini
        gemini_response = self._generate_gemini_response(user_input, research_needed)
        response["response_to_user"] = gemini_response
        
        # Determine next action for Qwen
        next_action = self._determine_next_action(user_input, gemini_response)
        response["next_action"] = next_action
        
        # Add assistant response to history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "assistant",
            "content": gemini_response
        })
        
        return response

    def _analyze_research_needs(self, user_input: str) -> bool:
        """Analyze if user input requires research."""
        research_keywords = [
            "similar projects", "github repos", "alternatives", "examples",
            "how to", "best practices", "tutorials", "documentation",
            "stack overflow", "find", "search", "compare", "like"
        ]
        
        user_lower = user_input.lower()
        return any(keyword in user_lower for keyword in research_keywords)

    def _conduct_research(self, query: str) -> Dict[str, Any]:
        """Conduct research using GitHub and Stack Overflow."""
        logger.log_agent_action("GEMINI", "RESEARCH", f"Researching: {query[:50]}...")
        
        research_results = {
            "queries": [],
            "github_repos": [],
            "stackoverflow_posts": [],
            "summary": ""
        }
        
        # Extract search terms from query
        search_terms = self._extract_search_terms(query)
        research_results["queries"] = search_terms
        
        # Search GitHub
        for term in search_terms[:3]:  # Limit to top 3 terms
            try:
                github_results = self.github_searcher.search_repositories(term)
                research_results["github_repos"].extend(github_results[:5])  # Top 5 per term
            except Exception as e:
                logger.error(f"GitHub search failed for '{term}': {e}")
        
        # Search Stack Overflow
        for term in search_terms[:2]:  # Limit to top 2 terms
            try:
                so_results = self.so_searcher.search_questions(term)
                research_results["stackoverflow_posts"].extend(so_results[:3])  # Top 3 per term
            except Exception as e:
                logger.error(f"Stack Overflow search failed for '{term}': {e}")
        
        # Generate research summary
        research_results["summary"] = self._summarize_research(research_results)
        
        # Cache results
        cache_key = hash(query)
        self.research_cache[cache_key] = research_results
        
        return research_results

    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract relevant search terms from user query."""
        # Remove common words and extract key terms
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        
        # Clean and tokenize
        clean_query = re.sub(r'[^\w\s]', '', query.lower())
        words = [word for word in clean_query.split() if word not in stop_words and len(word) > 2]
        
        # Extract phrases and important terms
        search_terms = []
        
        # Look for quoted phrases
        quoted_phrases = re.findall(r'"([^"]*)"', query)
        search_terms.extend(quoted_phrases)
        
        # Add important individual words
        important_words = [word for word in words if len(word) > 4]
        search_terms.extend(important_words[:3])
        
        # Add combined terms
        if len(words) >= 2:
            search_terms.append(" ".join(words[:2]))
        
        return list(set(search_terms))  # Remove duplicates

    def _summarize_research(self, research_results: Dict[str, Any]) -> str:
        """Generate a summary of research findings."""
        github_count = len(research_results["github_repos"])
        so_count = len(research_results["stackoverflow_posts"])
        
        summary = f"Research Summary:\n"
        summary += f"- Found {github_count} relevant GitHub repositories\n"
        summary += f"- Found {so_count} relevant Stack Overflow discussions\n"
        
        if github_count > 0:
            top_repo = research_results["github_repos"][0]
            summary += f"- Top repository: {top_repo['name']} ({top_repo['stars']} stars)\n"
        
        if so_count > 0:
            top_post = research_results["stackoverflow_posts"][0]
            summary += f"- Top Stack Overflow post: {top_post['title']}\n"
        
        return summary

    def _generate_gemini_response(self, user_input: str, has_research: bool) -> str:
        """Generate response using Gemini API."""
        try:
            # Build context
            context = self._build_context(user_input, has_research)
            
            prompt = f"""You are an intelligent coding assistant. Based on the context below, provide a helpful response to the user.

Context:
{context}

User Input: {user_input}

Provide a clear, helpful response that:
1. Acknowledges what the user is asking for
2. Incorporates relevant research findings if available
3. Suggests next steps or actions
4. Updates the plan if needed

Response:"""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return f"I encountered an issue generating a response. Error: {str(e)}"

    def _build_context(self, user_input: str, has_research: bool) -> str:
        """Build context for Gemini including plan and research."""
        context = f"Current Plan:\n{self.plan_manager.get_plan()}\n\n"
        
        if has_research and self.research_cache:
            latest_research = list(self.research_cache.values())[-1]
            context += f"Recent Research Findings:\n{latest_research['summary']}\n\n"
        
        # Add recent conversation history
        if len(self.conversation_history) > 0:
            context += "Recent Conversation:\n"
            for msg in self.conversation_history[-4:]:  # Last 4 messages
                role = msg["role"].title()
                content = msg["content"][:200]  # Truncate for context
                context += f"{role}: {content}\n"
        
        return context

    def _determine_next_action(self, user_input: str, response: str) -> str:
        """Determine what action Qwen should take next."""
        # Keywords that suggest code generation
        code_keywords = ["create", "build", "implement", "code", "write", "generate", "develop"]
        
        # Keywords that suggest file operations
        file_keywords = ["file", "directory", "folder", "save", "write to"]
        
        # Keywords that suggest CLI operations
        cli_keywords = ["install", "run", "execute", "command", "terminal", "bash"]
        
        user_lower = user_input.lower()
        
        if any(keyword in user_lower for keyword in code_keywords):
            return "code_generation"
        elif any(keyword in user_lower for keyword in file_keywords):
            return "file_operations"
        elif any(keyword in user_lower for keyword in cli_keywords):
            return "cli_operations"
        else:
            return "conversation_only"

    def _update_plan_with_research(self, research_results: Dict[str, Any]) -> None:
        """Update plan file with research findings."""
        if research_results["github_repos"] or research_results["stackoverflow_posts"]:
            update_text = f"Research conducted: {research_results['summary']}"
            self.plan_manager.update_plan(update_text)
            logger.log_plan_update("RESEARCH", update_text)

    def update_plan_manual(self, update_text: str, section: Optional[str] = None) -> None:
        """Manually update plan (called by user or other modules)."""
        self.plan_manager.update_plan(update_text, section)
        logger.log_plan_update("MANUAL", update_text)

    def get_plan_content(self) -> str:
        """Get current plan content for Qwen agent."""
        return self.plan_manager.get_plan()

    def get_conversation_context(self) -> List[Dict]:
        """Get conversation history for context."""
        return self.conversation_history[-10:]  # Last 10 messages

    def clear_conversation_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")
