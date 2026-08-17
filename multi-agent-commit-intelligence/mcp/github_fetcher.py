# root/mcp/github_fetche

import os
import requests
from typing import List, Dict, Any

def fetch_repo_commits_raw(repo_owner: str, repo_name: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Mengambil commit mentah dari GitHub untuk dianalisis oleh AI."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits?per_page={limit}"
    headers = {
        "Accept": "application/vnd.github+json", 
        "User-Agent": "Agno-Agent",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"  
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return [{"error": f"Gagal mengambil repo '{repo_owner}/{repo_name}': Status {response.status_code}"}]
        
        raw_commits = response.json()
        parsed_commits = []

        for c in raw_commits:
            sha = c.get("sha")
            commit_data = c.get("commit", {})
            author_info = commit_data.get("author", {})
            
            author_name = author_info.get("name") or "Unknown"
            author_email = author_info.get("email") or f"{author_name.lower().replace(' ', '')}@noemail.com"
            committed_at = author_info.get("date")
            message = commit_data.get("message", "").split("\n")[0]

            parsed_commits.append({
                "repo_owner": repo_owner,
                "repo_name": repo_name,
                "commit_sha": sha,
                "author_name": author_name,
                "author_email": author_email,
                "committed_at": committed_at,
                "commit_message": message
            })

        return parsed_commits
    except Exception as e:
        return [{"error": f"Error fetch GitHub: {str(e)}"}]
    