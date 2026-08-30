import httpx
from app.config import get_settings
from app.providers.base import LearningResourceProvider


class YouTubeProvider(LearningResourceProvider):
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self):
        self.api_key = get_settings().youtube_api_key

    def search_resources(self, query: str, skill: str = None, difficulty: str = None, limit: int = 10, **kwargs) -> list[dict]:
        search_query = query
        if skill:
            search_query = f"{skill} {query} tutorial"
        if difficulty:
            search_query += f" {difficulty}"

        params = {
            "part": "snippet",
            "q": search_query,
            "type": "video",
            "maxResults": min(limit, 25),
            "key": self.api_key,
            "relevanceLanguage": "en",
            "videoCategoryId": "27",  # Education
            "order": "relevance",
        }

        with httpx.Client(timeout=15.0) as client:
            response = client.get(f"{self.BASE_URL}/search", params=params)
            if response.status_code != 200:
                return []

            data = response.json()
            results = []

            video_ids = [item["id"]["videoId"] for item in data.get("items", []) if item["id"].get("videoId")]

            # Get video details for duration
            details = {}
            if video_ids:
                detail_params = {
                    "part": "contentDetails,statistics",
                    "id": ",".join(video_ids),
                    "key": self.api_key,
                }
                detail_response = client.get(f"{self.BASE_URL}/videos", params=detail_params)
                if detail_response.status_code == 200:
                    for item in detail_response.json().get("items", []):
                        details[item["id"]] = {
                            "duration": item.get("contentDetails", {}).get("duration", ""),
                            "view_count": item.get("statistics", {}).get("viewCount", "0"),
                        }

            for item in data.get("items", []):
                video_id = item["id"].get("videoId")
                if not video_id:
                    continue

                snippet = item["snippet"]
                detail = details.get(video_id, {})

                results.append({
                    "provider": "youtube",
                    "external_id": video_id,
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", ""),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                    "resource_type": "video",
                    "difficulty": difficulty or "intermediate",
                    "duration": self._parse_duration(detail.get("duration", "")),
                    "metadata": {
                        "channel": snippet.get("channelTitle", ""),
                        "published_at": snippet.get("publishedAt", ""),
                        "view_count": detail.get("view_count", "0"),
                    },
                })

            return results

    def get_resource(self, external_id: str) -> dict | None:
        params = {
            "part": "snippet,contentDetails,statistics",
            "id": external_id,
            "key": self.api_key,
        }

        with httpx.Client() as client:
            response = client.get(f"{self.BASE_URL}/videos", params=params)
            if response.status_code != 200:
                return None

            items = response.json().get("items", [])
            if not items:
                return None

            item = items[0]
            snippet = item["snippet"]

            return {
                "provider": "youtube",
                "external_id": external_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "url": f"https://www.youtube.com/watch?v={external_id}",
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "resource_type": "video",
                "duration": self._parse_duration(item.get("contentDetails", {}).get("duration", "")),
                "metadata": {
                    "channel": snippet.get("channelTitle", ""),
                    "published_at": snippet.get("publishedAt", ""),
                    "view_count": item.get("statistics", {}).get("viewCount", "0"),
                },
            }

    def _parse_duration(self, iso_duration: str) -> str:
        if not iso_duration:
            return ""
        # Parse ISO 8601 duration (PT1H2M3S)
        import re
        match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_duration)
        if not match:
            return iso_duration
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
