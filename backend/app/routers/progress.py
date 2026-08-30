from fastapi import APIRouter
from app.services.supabase_service import SupabaseService

router = APIRouter()


@router.get("/{user_id}")
async def get_progress(user_id: str):
    db = SupabaseService()
    progress = await db.get_user_progress(user_id)
    return progress


@router.post("/complete")
async def mark_complete(user_id: str, segment_id: str = None, resource_id: str = None):
    db = SupabaseService()
    result = await db.mark_progress(user_id, segment_id=segment_id, resource_id=resource_id)
    return result


@router.get("/dashboard/{user_id}")
async def get_dashboard_data(user_id: str):
    db = SupabaseService()
    progress = await db.get_user_progress(user_id)
    skills = await db.get_user_skills(user_id)
    path = await db.get_learning_path(user_id)
    return {
        "progress": progress,
        "skills": skills,
        "learning_path": path,
    }
