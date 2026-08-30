import threading
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import GoalCreate, GoalAnalysis, OnboardingData
from app.services.ai_service import AIService
from app.config import get_settings

router = APIRouter()


@router.post("/analyze")
def analyze_goal(data: GoalCreate):
    ai = AIService()
    analysis = ai.analyze_goal(data.raw_goal)
    return analysis


def _generate_roadmap_background(goal_id: str):
    try:
        from app.services.roadmap_generator import RoadmapGenerator
        generator = RoadmapGenerator()
        result = generator.generate(goal_id)
        print(f"Background roadmap generated: {result.get('title', 'unknown')}")
    except Exception as e:
        print(f"Background roadmap generation failed: {e}")


@router.post("/onboarding")
def complete_onboarding(data: OnboardingData, user_id: str = None):
    from app.services.supabase_service import SupabaseService
    db = SupabaseService()

    uid = user_id or data.user_id
    if not uid or len(uid) < 10:
        raise HTTPException(status_code=400, detail="user_id is required (must be a valid UUID)")

    profile = db.create_profile(uid, data.profile)
    if data.interests:
        db.save_interests(uid, data.interests)
    if data.skills:
        db.save_user_skills(uid, data.skills)

    goal_id = None
    if data.goal:
        goal = db.create_goal(uid, data.goal)
        goal_id = goal.get("id")

        # Generate roadmap in background thread so onboarding returns fast
        thread = threading.Thread(target=_generate_roadmap_background, args=(goal_id,))
        thread.start()

    return {
        "profile": profile,
        "goal_id": goal_id,
        "status": "onboarding_complete",
        "roadmap_status": "generating" if goal_id else "no_goal",
    }


@router.get("/roadmap-status/{user_id}")
def check_roadmap_status(user_id: str):
    from app.services.supabase_service import SupabaseService
    db = SupabaseService()
    path = db.get_learning_path(user_id)
    if path:
        return {"status": "ready", "title": path.get("title", ""), "segments": len(path.get("segments", []))}
    return {"status": "generating"}
