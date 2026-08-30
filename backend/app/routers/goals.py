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


@router.post("/onboarding")
def complete_onboarding(data: OnboardingData, user_id: str = None):
    ai = AIService()
    from app.services.supabase_service import SupabaseService
    from app.services.roadmap_generator import RoadmapGenerator
    db = SupabaseService()

    # Priority: query param > body field
    uid = user_id or data.user_id
    if not uid or len(uid) < 10:
        raise HTTPException(status_code=400, detail="user_id is required (must be a valid UUID)")

    profile = db.create_profile(uid, data.profile)
    if data.interests:
        db.save_interests(uid, data.interests)
    if data.skills:
        db.save_user_skills(uid, data.skills)

    if data.goal:
        goal = db.create_goal(uid, data.goal)
        goal_id = goal.get("id")

        # Auto-generate roadmap
        try:
            generator = RoadmapGenerator()
            roadmap = generator.generate(goal_id)
        except Exception as e:
            print(f"Roadmap generation failed: {e}")
            roadmap = None

        try:
            analysis = ai.analyze_goal(data.goal)
        except Exception as e:
            print(f"Goal analysis failed: {e}")
            analysis = {"goal": data.goal, "target_skills": [], "suggested_milestones": []}

        return {
            "profile": profile,
            "goal_analysis": analysis,
            "goal_id": goal_id,
            "roadmap": roadmap,
        }

    return {"profile": profile}
