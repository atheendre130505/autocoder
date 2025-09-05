# github_utils.py
from github import Github
import os
from typing import List, Dict

def get_github_client():
    return Github(os.environ["GITHUB_API_TOKEN"])

def fetch_readme(repo: str):
    g = get_github_client()
    repository = g.get_repo(repo)
    return repository.get_readme().decoded_content.decode()

def research_similar_projects(task: str, max_results: int = 5) -> List[Dict]:
    """Basic implementation - searches GitHub for repositories"""
    try:
        g = get_github_client()
        # Simple keyword search
        query = f"{task} language:python"
        repos = g.search_repositories(query)
        
        results = []
        for repo in repos[:max_results]:
            results.append({
                'name': repo.name,
                'description': repo.description,
                'url': repo.html_url,
                'stars': repo.stargazers_count
            })
        return results
    except Exception as e:
        print(f"GitHub search error: {e}")
        return []

def extract_code_patterns(repo: str, file_extensions: List[str] = [".py"]) -> Dict:
    """Basic implementation"""
    return {"patterns": f"Code patterns for {repo}"}

def get_project_context(task: str) -> Dict:
    """Basic implementation"""
    similar_projects = research_similar_projects(task)
    return {"similar_projects": similar_projects, "task": task}
