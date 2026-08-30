from fastapi import APIRouter, HTTPException
from app.services.supabase_service import SupabaseService

router = APIRouter()


@router.get("/")
async def list_skills(category: str = None):
    db = SupabaseService()
    skills = await db.get_skills(category)
    return skills


@router.get("/prerequisites/{skill_id}")
async def get_prerequisites(skill_id: str):
    db = SupabaseService()
    prereqs = await db.get_skill_prerequisites(skill_id)
    return prereqs


@router.get("/gap/{user_id}")
async def get_skill_gaps(user_id: str):
    from app.services.skill_gap_engine import SkillGapEngine
    engine = SkillGapEngine()
    gaps = await engine.compute_gaps(user_id)
    return gaps
