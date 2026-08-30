from app.services.supabase_service import SupabaseService
from app.services.ai_service import AIService


LEVEL_MAP = {"beginner": 1, "intermediate": 2, "advanced": 3}
GAP_LABELS = {0: "none", 1: "low", 2: "medium", 3: "high"}


class SkillGapEngine:
    def __init__(self):
        self.db = SupabaseService()
        self.ai = AIService()

    def compute_gaps(self, user_id: str) -> list[dict]:
        user_skills = self.db.get_user_skills(user_id)
        profile = self.db.get_profile(user_id)
        if not profile:
            return []

        # Get active goal
        goals = self.db.client.table("goals").select("*").eq("user_id", user_id).eq("status", "active").execute()
        if not goals.data:
            return []

        goal = goals.data[0]
        goal_skills = self.db.client.table("goal_skills").select(
            "*, skills(name)"
        ).eq("goal_id", goal["id"]).execute()

        # Build current skill map
        current_map = {}
        for us in user_skills:
            skill_name = us.get("skills", {}).get("name", "") if isinstance(us.get("skills"), dict) else ""
            if skill_name:
                current_map[skill_name.lower()] = {
                    "level": us.get("current_level", "beginner"),
                    "confidence": us.get("confidence", 1),
                }

        # Compute gaps
        gaps = []
        for gs in (goal_skills.data or []):
            skill_name = gs.get("skills", {}).get("name", "") if isinstance(gs.get("skills"), dict) else ""
            if not skill_name:
                continue

            required_level = gs.get("required_level", "intermediate")
            current = current_map.get(skill_name.lower(), {"level": "beginner", "confidence": 1})

            current_num = LEVEL_MAP.get(current["level"], 0)
            target_num = LEVEL_MAP.get(required_level, 2)
            gap_num = max(0, target_num - current_num)

            gaps.append({
                "skill_name": skill_name,
                "skill_id": gs.get("skill_id", ""),
                "current_level": current["level"],
                "target_level": required_level,
                "gap": GAP_LABELS.get(gap_num, "high"),
                "importance": gs.get("importance", 0.5),
                "prerequisites": [],
                "recommended_action": self._get_action(gap_num, skill_name),
            })

        # Sort by importance and gap severity
        gaps.sort(key=lambda g: (["none", "low", "medium", "high", "critical"].index(g["gap"]), -g["importance"]), reverse=True)
        return gaps

    def _get_action(self, gap: int, skill: str) -> str:
        if gap == 0:
            return f"Maintain proficiency in {skill}"
        elif gap == 1:
            return f"Practice advanced concepts in {skill}"
        elif gap == 2:
            return f"Study {skill} fundamentals and build projects"
        else:
            return f"Start learning {skill} from scratch with beginner resources"
