from fastapi import APIRouter
from app.services.recommendation_engine import RecommendationEngine

router = APIRouter()


@router.get("/{user_id}")
async def get_recommendations(user_id: str, limit: int = 10):
    engine = RecommendationEngine()
    recommendations = await engine.get_recommendations(user_id, limit=limit)
    return recommendations


@router.get("/{user_id}/next-actions")
async def get_next_actions(user_id: str):
    engine = RecommendationEngine()
    actions = await engine.get_next_actions(user_id)
    return actions
