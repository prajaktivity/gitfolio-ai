import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.core.config import settings


GITHUB_API_BASE = "https://api.github.com"
LANGUAGE_COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#2b7489",
    "Java": "#b07219", "Go": "#00ADD8", "Rust": "#dea584", "C++": "#f34b7d",
    "C": "#555555", "Ruby": "#701516", "PHP": "#4F5D95", "Swift": "#ffac45",
    "Kotlin": "#F18E33", "Dart": "#00B4AB", "HTML": "#e34c26", "CSS": "#563d7c",
    "Shell": "#89e051", "Dockerfile": "#384d54", "Vue": "#2c3e50", "React": "#61dafb",
}


class GitHubService:
    def __init__(self, access_token: str):
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_user(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{GITHUB_API_BASE}/user", headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def get_all_repos(self, username: str) -> List[Dict[str, Any]]:
        repos = []
        page = 1
        async with httpx.AsyncClient() as client:
            while True:
                resp = await client.get(
                    f"{GITHUB_API_BASE}/users/{username}/repos",
                    headers=self.headers,
                    params={"per_page": 100, "page": page, "sort": "updated", "type": "owner"},
                )
                resp.raise_for_status()
                batch = resp.json()
                if not batch:
                    break
                repos.extend(batch)
                page += 1
                if len(batch) < 100:
                    break
        return repos

    async def get_repo_languages(self, owner: str, repo: str) -> Dict[str, int]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GITHUB_API_BASE}/repos/{owner}/{repo}/languages",
                headers=self.headers,
            )
            if resp.status_code == 200:
                return resp.json()
            return {}

    async def get_commit_count(self, owner: str, repo: str) -> int:
        async with httpx.AsyncClient() as client:
            # Use the contributors endpoint for faster count
            resp = await client.get(
                f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contributors",
                headers=self.headers,
                params={"per_page": 1, "anon": "true"},
            )
            if resp.status_code != 200:
                return 0
            # Check link header for total pages (= commit count approximation)
            link_header = resp.headers.get("link", "")
            if 'rel="last"' in link_header:
                import re
                match = re.search(r'page=(\d+)>; rel="last"', link_header)
                if match:
                    return int(match.group(1))
            return len(resp.json())

    async def get_contribution_stats(self, username: str) -> Dict[str, Any]:
        """Get contribution data via GraphQL for accurate stats."""
        query = """
        query($username: String!) {
          user(login: $username) {
            contributionsCollection {
              totalCommitContributions
              totalPullRequestContributions
              totalIssueContributions
              contributionCalendar {
                totalContributions
                weeks {
                  contributionDays {
                    contributionCount
                    date
                  }
                }
              }
            }
          }
        }
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.github.com/graphql",
                headers=self.headers,
                json={"query": query, "variables": {"username": username}},
            )
            if resp.status_code == 200:
                data = resp.json()
                collection = data.get("data", {}).get("user", {}).get("contributionsCollection", {})
                return {
                    "total_commits": collection.get("totalCommitContributions", 0),
                    "total_prs": collection.get("totalPullRequestContributions", 0),
                    "total_issues": collection.get("totalIssueContributions", 0),
                    "total_contributions": collection.get("contributionCalendar", {}).get("totalContributions", 0),
                    "calendar": collection.get("contributionCalendar", {}).get("weeks", []),
                }
        return {}

    async def analyze_profile(self, username: str) -> Dict[str, Any]:
        """Full profile analysis — aggregates all GitHub data."""
        # Get user info
        user_data = await self.get_user()
        
        # Get all repos
        repos = await self.get_all_repos(username)
        non_forked = [r for r in repos if not r.get("fork", False)]
        
        # Aggregate language bytes across all repos
        all_languages: Dict[str, int] = {}
        top_repos_data = []

        # Process top 10 repos for language data (avoid rate limits)
        sorted_repos = sorted(non_forked, key=lambda r: r.get("stargazers_count", 0), reverse=True)
        
        for repo in sorted_repos[:10]:
            lang_data = await self.get_repo_languages(username, repo["name"])
            for lang, bytes_count in lang_data.items():
                all_languages[lang] = all_languages.get(lang, 0) + bytes_count

        # Build top repos list
        for repo in sorted_repos[:6]:
            top_repos_data.append({
                "name": repo["name"],
                "description": repo.get("description"),
                "url": repo.get("html_url"),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "language": repo.get("language"),
                "topics": repo.get("topics", []),
                "updated_at": repo.get("updated_at"),
            })

        # Calculate language percentages
        total_bytes = sum(all_languages.values())
        top_languages = []
        if total_bytes > 0:
            for lang, bytes_count in sorted(all_languages.items(), key=lambda x: x[1], reverse=True)[:8]:
                top_languages.append({
                    "name": lang,
                    "percentage": round((bytes_count / total_bytes) * 100, 1),
                    "bytes": bytes_count,
                    "color": LANGUAGE_COLORS.get(lang, "#8b8b8b"),
                })

        # Get contribution stats
        contrib_stats = await self.get_contribution_stats(username)

        # Detect skill tags from languages, topics, repo names
        skill_tags = set()
        for lang in all_languages.keys():
            skill_tags.add(lang)
        for repo in repos[:20]:
            for topic in repo.get("topics", []):
                skill_tags.add(topic.title())
        
        # Add framework detection
        framework_keywords = {
            "fastapi", "django", "flask", "react", "nextjs", "vue", "angular",
            "docker", "kubernetes", "aws", "gcp", "firebase", "postgres", 
            "mongodb", "redis", "graphql", "rest-api", "machine-learning",
            "deep-learning", "tensorflow", "pytorch", "scikit-learn"
        }
        for repo in repos[:20]:
            repo_name = repo.get("name", "").lower()
            description = (repo.get("description") or "").lower()
            for kw in framework_keywords:
                if kw in repo_name or kw in description:
                    skill_tags.add(kw.title().replace("-", " "))

        # Account age
        created_at = datetime.fromisoformat(user_data.get("created_at", "").replace("Z", "+00:00"))
        age_days = (datetime.now(created_at.tzinfo) - created_at).days

        return {
            "github_id": user_data.get("id"),
            "github_username": username,
            "name": user_data.get("name"),
            "email": user_data.get("email"),
            "avatar_url": user_data.get("avatar_url"),
            "public_repos": user_data.get("public_repos", 0),
            "followers": user_data.get("followers", 0),
            "following": user_data.get("following", 0),
            "total_stars": sum(r.get("stargazers_count", 0) for r in non_forked),
            "total_forks": sum(r.get("forks_count", 0) for r in non_forked),
            "total_commits": contrib_stats.get("total_commits", 0),
            "account_age_days": age_days,
            "top_languages": top_languages,
            "top_repos": top_repos_data,
            "contribution_data": {
                "total_contributions": contrib_stats.get("total_contributions", 0),
                "total_prs": contrib_stats.get("total_prs", 0),
                "total_issues": contrib_stats.get("total_issues", 0),
            },
            "skill_tags": list(skill_tags)[:20],
        }


async def exchange_code_for_token(code: str) -> Optional[str]:
    """Exchange OAuth code for GitHub access token."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("access_token")
    return None
