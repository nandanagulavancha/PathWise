import httpx
from app.config import get_settings
from app.providers.base import LearningResourceProvider


class GitHubProvider(LearningResourceProvider):
    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.token = get_settings().github_token

    async def search_resources(self, query: str, skill: str = None, limit: int = 10, **kwargs) -> list[dict]:
        search_query = query
        if skill:
            search_query = f"{skill} {query}"

        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"

        params = {
            "q": f"{search_query} stars:>50",
            "sort": "stars",
            "order": "desc",
            "per_page": min(limit, 30),
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/search/repositories", params=params, headers=headers)
            if response.status_code != 200:
                return []

            data = response.json()
            results = []

            for item in data.get("items", []):
                results.append({
                    "provider": "github",
                    "external_id": str(item["id"]),
                    "title": item.get("full_name", ""),
                    "description": item.get("description", ""),
                    "url": item.get("html_url", ""),
                    "thumbnail": item.get("owner", {}).get("avatar_url", ""),
                    "resource_type": "repository",
                    "difficulty": "intermediate",
                    "metadata": {
                        "stars": item.get("stargazers_count", 0),
                        "language": item.get("language", ""),
                        "topics": item.get("topics", []),
                        "updated_at": item.get("updated_at", ""),
                    },
                })

            return results

    async def get_resource(self, external_id: str) -> dict | None:
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/repositories/{external_id}", headers=headers)
            if response.status_code != 200:
                return None

            item = response.json()
            return {
                "provider": "github",
                "external_id": str(item["id"]),
                "title": item.get("full_name", ""),
                "description": item.get("description", ""),
                "url": item.get("html_url", ""),
                "thumbnail": item.get("owner", {}).get("avatar_url", ""),
                "resource_type": "repository",
                "metadata": {
                    "stars": item.get("stargazers_count", 0),
                    "language": item.get("language", ""),
                    "topics": item.get("topics", []),
                },
            }
