from fastapi import APIRouter, HTTPException
from app.models.schemas import RoadmapGenerateRequest
from app.services.roadmap_generator import RoadmapGenerator

router = APIRouter()


@router.post("/generate")
async def generate_roadmap(data: RoadmapGenerateRequest):
    generator = RoadmapGenerator()
    roadmap = await generator.generate(data.goal_id)
    return roadmap


@router.get("/{user_id}")
async def get_roadmap(user_id: str):
    from app.services.supabase_service import SupabaseService
    db = SupabaseService()
    roadmap = await db.get_learning_path(user_id)
    if not roadmap:
        raise HTTPException(status_code=404, detail="No roadmap found")
    return roadmap


@router.post("/adapt/{path_id}")
async def adapt_roadmap(path_id: str):
    from app.services.adaptive_engine import AdaptiveEngine
    engine = AdaptiveEngine()
    result = await engine.adapt(path_id)
    return result
