import requests
from typing import List, Dict
import time
from urllib.parse import quote

from core import logger

class StackOverflowSearcher:
    """Stack Overflow API integration for searching questions and answers."""
    
    def __init__(self):
        self.base_url = "https://api.stackexchange.com/2.3"
        self.site = "stackoverflow"

    def search_questions(self, query: str, limit: int = 10) -> List[Dict]:
        """Search Stack Overflow questions by query."""
        try:
            # Build search URL
            search_url = f"{self.base_url}/search/advanced"
            params = {
                "order": "desc",
                "sort": "votes",
                "q": query,
                "site": self.site,
                "pagesize": min(limit, 100)
            }
            
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            questions = []
            for item in data.get("items", []):
                questions.append({
                    "title": item.get("title", ""),
                    "score": item.get("score", 0),
                    "view_count": item.get("view_count", 0),
                    "answer_count": item.get("answer_count", 0),
                    "url": item.get("link", ""),
                    "tags": item.get("tags", []),
                    "is_answered": item.get("is_answered", False),
                    "creation_date": item.get("creation_date", 0)
                })
            
            logger.info(f"Found {len(questions)} Stack Overflow questions for: {query}")
            return questions
            
        except requests.RequestException as e:
            logger.error(f"Stack Overflow API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Stack Overflow search failed: {e}")
            return []

    def search_by_tags(self, tags: List[str], limit: int = 5) -> List[Dict]:
        """Search questions by specific tags."""
        try:
            search_url = f"{self.base_url}/questions"
            params = {
                "order": "desc",
                "sort": "votes",
                "tagged": ";".join(tags),
                "site": self.site,
                "pagesize": min(limit, 100)
            }
            
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            questions = []
            for item in data.get("items", []):
                questions.append({
                    "title": item.get("title", ""),
                    "score": item.get("score", 0),
                    "tags": item.get("tags", []),
                    "url": item.get("link", ""),
                    "is_answered": item.get("is_answered", False)
                })
            
            return questions
            
        except Exception as e:
            logger.error(f"Stack Overflow tag search failed: {e}")
            return []

    def get_coding_solutions(self, problem_type: str) -> List[Dict]:
        """Get solutions for specific coding problems."""
        tag_mappings = {
            "cli": ["command-line", "terminal", "cli"],
            "ai": ["artificial-intelligence", "machine-learning", "nlp"],
            "automation": ["automation", "scripting", "batch-processing"],
            "api": ["api", "rest", "web-services"]
        }
        
        tags = tag_mappings.get(problem_type, [problem_type])
        return self.search_by_tags(tags, 5)
