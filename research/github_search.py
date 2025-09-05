import requests
from typing import List, Dict, Optional
import time

from core import config, logger

class GitHubSearcher:
    """GitHub API integration for repository searches."""
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Autocoder-Research-Tool"
        }
        
        if config.GITHUB_API_TOKEN:
            self.headers["Authorization"] = f"token {config.GITHUB_API_TOKEN}"
            logger.info("GitHub API initialized with authentication")
        else:
            logger.warning("GitHub API initialized without authentication (rate limited)")

    def search_repositories(self, query: str, limit: int = 10) -> List[Dict]:
        """Search GitHub repositories by query."""
        try:
            # Build search query
            search_url = f"{self.base_url}/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": min(limit, 100)
            }
            
            response = requests.get(search_url, headers=self.headers, params=params)
            
            if response.status_code == 403:
                logger.error("GitHub API rate limit exceeded")
                return []
            
            response.raise_for_status()
            data = response.json()
            
            repositories = []
            for repo in data.get("items", []):
                repositories.append({
                    "name": repo["full_name"],
                    "description": repo["description"] or "No description",
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "language": repo["language"] or "Unknown",
                    "url": repo["html_url"],
                    "topics": repo.get("topics", []),
                    "updated": repo["updated_at"]
                })
            
            logger.info(f"Found {len(repositories)} repositories for query: {query}")
            return repositories
            
        except requests.RequestException as e:
            logger.error(f"GitHub API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"GitHub search failed: {e}")
            return []

    def get_repository_details(self, owner: str, repo: str) -> Optional[Dict]:
        """Get detailed information about a specific repository."""
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            repo_data = response.json()
            return {
                "name": repo_data["full_name"],
                "description": repo_data["description"],
                "stars": repo_data["stargazers_count"],
                "forks": repo_data["forks_count"],
                "language": repo_data["language"],
                "topics": repo_data.get("topics", []),
                "readme_url": f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
            }
            
        except requests.RequestException as e:
            logger.error(f"Failed to get repository details: {e}")
            return None

    def search_by_topic(self, topic: str, limit: int = 5) -> List[Dict]:
        """Search repositories by specific topic."""
        query = f"topic:{topic}"
        return self.search_repositories(query, limit)

    def search_coding_tools(self, tool_type: str) -> List[Dict]:
        """Search for specific types of coding tools."""
        queries = {
            "autocoder": "autocoder OR auto-coder OR automatic coding",
            "cli-tools": "cli tool coding OR terminal coding assistant",
            "copilot": "github copilot alternative OR AI code completion",
            "code-generation": "code generation AI OR LLM code generator"
        }
        
        query = queries.get(tool_type, tool_type)
        return self.search_repositories(query, 10)
