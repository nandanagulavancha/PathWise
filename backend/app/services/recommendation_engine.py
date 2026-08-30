from app.services.supabase_service import SupabaseService
from app.services.embedding_service import EmbeddingService


class RecommendationEngine:
    def __init__(self):
        self.db = SupabaseService()
        self.embedding_service = EmbeddingService()

    async def get_recommendations(self, user_id: str, limit: int = 10) -> list[dict]:
        profile = await self.db.get_profile(user_id)
        if not profile:
            return []

        user_skills = await self.db.get_user_skills(user_id)
        path = await self.db.get_learning_path(user_id)

        # Get current segment resources
        if path and path.get("segments"):
            current_segments = [s for s in path["segments"] if s.get("status") in ("in_progress", "upcoming")]
            if current_segments:
                segment = current_segments[0]
                resources = segment.get("segment_resources", [])
                scored = []
                for r in resources:
                    resource = r.get("resources", r)
                    score = self._compute_score(resource, profile, user_skills)
                    scored.append({**resource, "recommendation_score": score["total"], "recommendation_reason": score["reason"]})
                scored.sort(key=lambda x: x.get("recommendation_score", 0), reverse=True)
                return scored[:limit]

        return []

    async def get_next_actions(self, user_id: str) -> list[dict]:
        path = await self.db.get_learning_path(user_id)
        actions = []

        if not path:
            actions.append({"type": "onboarding", "title": "Complete your profile", "description": "Set up your learning goals to get started"})
            return actions

        segments = path.get("segments", [])
        current = next((s for s in segments if s.get("status") == "in_progress"), None)

        if current:
            actions.append({
                "type": "continue",
                "title": f"Continue: {current.get('title', 'Current segment')}",
                "description": "Pick up where you left off",
                "segment_id": current.get("id"),
            })

        # Check for pending quizzes
        for s in segments:
            if s.get("status") == "in_progress":
                actions.append({
                    "type": "quiz",
                    "title": f"Take Reflection Quiz: {s.get('title', '')}",
                    "description": "Test your understanding",
                    "segment_id": s.get("id"),
                })
                break

        return actions[:5]

    def _compute_score(self, resource: dict, profile: dict, user_skills: list) -> dict:
        scores = {
            "semantic_similarity": 0.7,
            "skill_gap_relevance": 0.8,
            "prerequisite_fit": 0.9,
            "learner_level_fit": self._level_fit(resource, profile),
            "goal_alignment": 0.8,
            "learning_preference_fit": self._preference_fit(resource, profile),
            "resource_quality": 0.7,
            "difficulty_fit": self._difficulty_fit(resource, profile),
            "feedback_adjustment": 0.0,
        }

        weights = {
            "semantic_similarity": 0.15,
            "skill_gap_relevance": 0.20,
            "prerequisite_fit": 0.15,
            "learner_level_fit": 0.10,
            "goal_alignment": 0.15,
            "learning_preference_fit": 0.05,
            "resource_quality": 0.10,
            "difficulty_fit": 0.10,
            "feedback_adjustment": 0.00,
        }

        total = sum(scores[k] * weights[k] for k in scores)
        reason = f"Recommended based on skill gap relevance ({scores['skill_gap_relevance']:.0%}) and goal alignment ({scores['goal_alignment']:.0%})"

        return {"total": round(total, 3), "reason": reason, **scores}

    def _level_fit(self, resource: dict, profile: dict) -> float:
        difficulty = resource.get("difficulty", "intermediate")
        level = profile.get("experience_level", "beginner")
        if difficulty == level:
            return 1.0
        return 0.6

    def _preference_fit(self, resource: dict, profile: dict) -> float:
        pref = profile.get("preferred_learning_style", "video")
        rtype = resource.get("resource_type", "video")
        return 1.0 if pref == rtype else 0.5

    def _difficulty_fit(self, resource: dict, profile: dict) -> float:
        return 0.8
