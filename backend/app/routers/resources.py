from fastapi import APIRouter, Query
from app.services.supabase_service import SupabaseService
from app.providers.youtube import YouTubeProvider
from app.providers.github import GitHubProvider

router = APIRouter()


@router.get("/search")
async def search_resources(
    query: str,
    skill: str = None,
    difficulty: str = None,
    provider: str = "youtube",
    limit: int = Query(default=10, le=50),
):
    if provider == "youtube":
        p = YouTubeProvider()
        results = await p.search_resources(query, skill=skill, difficulty=difficulty, limit=limit)
    elif provider == "github":
        p = GitHubProvider()
        results = await p.search_resources(query, skill=skill, limit=limit)
    else:
        results = []
    return results


@router.get("/{resource_id}")
async def get_resource(resource_id: str):
    db = SupabaseService()
    resource = await db.get_resource(resource_id)
    return resource


@router.get("/{resource_id}/explanation")
async def get_recommendation_explanation(resource_id: str, user_id: str):
    from app.services.ai_service import AIService
    ai = AIService()
    explanation = await ai.explain_recommendation(resource_id, user_id)
    return {"explanation": explanation}
