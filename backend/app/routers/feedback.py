from fastapi import APIRouter
from app.models.schemas import FeedbackCreate
from app.services.supabase_service import SupabaseService

router = APIRouter()


@router.post("/")
async def submit_feedback(user_id: str, data: FeedbackCreate):
    db = SupabaseService()
    result = await db.save_feedback(user_id, data)
    # Trigger adaptive engine if needed
    from app.services.adaptive_engine import AdaptiveEngine
    engine = AdaptiveEngine()
    await engine.process_feedback(user_id, data)
    return result


@router.get("/{user_id}")
async def get_feedback_history(user_id: str):
    db = SupabaseService()
    history = await db.get_feedback(user_id)
    return history
