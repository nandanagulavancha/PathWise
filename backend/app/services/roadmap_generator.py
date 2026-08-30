from app.services.supabase_service import SupabaseService
from app.services.ai_service import AIService
from app.services.skill_gap_engine import SkillGapEngine
from app.providers.youtube import YouTubeProvider
from app.providers.github import GitHubProvider


class RoadmapGenerator:
    def __init__(self):
        self.db = SupabaseService()
        self.ai = AIService()
        self.skill_gap = SkillGapEngine()
        self.youtube = YouTubeProvider()
        self.github = GitHubProvider()

    async def generate(self, goal_id: str) -> dict:
        goal = await self.db.get_goal(goal_id)
        if not goal:
            return {"error": "Goal not found"}

        user_id = goal["user_id"]
        profile = await self.db.get_profile(user_id)
        if not profile:
            return {"error": "Profile not found"}

        # Analyze goal with AI
        goal_analysis = await self.ai.analyze_goal(goal["raw_goal"])

        # Compute skill gaps
        gaps = await self.skill_gap.compute_gaps(user_id)

        # Generate roadmap structure
        phases = await self.ai.generate_roadmap_structure(goal_analysis, gaps, profile)
        if not phases:
            return {"error": "Failed to generate roadmap structure"}

        # Create learning path
        path_data = {
            "user_id": user_id,
            "goal_id": goal_id,
            "title": goal_analysis.get("target_role", goal["raw_goal"][:100]),
            "description": goal_analysis.get("goal", ""),
            "estimated_duration": f"{len(phases) * 2} weeks",
            "status": "active",
            "version": 1,
        }
        path = await self.db.save_learning_path(path_data)
        path_id = path.get("id", "temp")

        # Create segments with resources
        segments = []
        for idx, phase in enumerate(phases):
            # Search for resources in progressive difficulty order
            resources = []
            phase_skills = phase.get("skills", [phase["title"]])
            main_topic = phase_skills[0] if phase_skills else phase["title"]

            # Progressive difficulty queries: intro → core → applied
            difficulty_queries = [
                (f"{main_topic} beginner introduction tutorial explained", "beginner"),
                (f"{main_topic} complete tutorial step by step", "intermediate"),
                (f"{main_topic} advanced project tutorial", "advanced"),
            ]

            for query, difficulty in difficulty_queries:
                try:
                    yt_results = await self.youtube.search_resources(query, difficulty=difficulty, limit=2)
                    for r in yt_results:
                        if not any(existing.get("external_id") == r.get("external_id") for existing in resources):
                            r["difficulty"] = difficulty
                            resources.append(r)
                except Exception as e:
                    print(f"YouTube search failed for '{query}': {e}")
                if len(resources) >= 5:
                    break

            # Sort: beginner first, then intermediate, then advanced
            difficulty_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
            resources.sort(key=lambda r: difficulty_order.get(r.get("difficulty", "intermediate"), 1))

            # Save top 5 resources
            saved_resources = []
            for r in resources[:5]:
                saved = await self.db.save_resource(r)
                saved_resources.append(saved)

            # Create segment
            status = "in_progress" if idx == 0 else ("upcoming" if idx == 1 else "locked")
            segment_data = {
                "learning_path_id": path_id,
                "title": phase["title"],
                "overview": phase.get("objective", ""),
                "sequence": idx + 1,
                "estimated_duration": phase.get("estimated_duration", "1-2 weeks"),
                "status": status,
            }
            segment = await self.db.save_learning_segment(segment_data)
            segment["resources"] = saved_resources
            segments.append(segment)

            # Link resources to segment with sequence order
            for i, r in enumerate(saved_resources):
                if r.get("id") and segment.get("id"):
                    difficulty = r.get("difficulty", "intermediate")
                    self.db.client.table("segment_resources").insert({
                        "segment_id": segment["id"],
                        "resource_id": r["id"],
                        "sequence": i + 1,
                        "recommendation_score": 0.9 - (i * 0.05),
                        "recommendation_reason": f"Step {i+1}: {difficulty} level - progressive learning for {phase['title']}",
                    }).execute()

        path["segments"] = segments
        return path
