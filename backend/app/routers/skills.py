from fastapi import APIRouter, HTTPException
from app.services.supabase_service import SupabaseService

router = APIRouter()


@router.get("/")
def list_skills(category: str = None):
    db = SupabaseService()
    return db.get_skills_sync(category)


@router.get("/prerequisites/{skill_id}")
def get_prerequisites(skill_id: str):
    db = SupabaseService()
    return db.get_skill_prerequisites_sync(skill_id)


@router.get("/gap/{user_id}")
def get_skill_gaps(user_id: str):
    from app.services.skill_gap_engine import SkillGapEngine
    engine = SkillGapEngine()
    return engine.compute_gaps_sync(user_id)
