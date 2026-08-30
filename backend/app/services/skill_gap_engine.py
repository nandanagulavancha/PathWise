from app.services.supabase_service import SupabaseService
from app.services.ai_service import AIService

LEVEL_MAP = {"beginner": 1, "intermediate": 2, "advanced": 3}
GAP_LABELS = {0: "none", 1: "low", 2: "medium", 3: "high"}


class SkillGapEngine:
    def __init__(self):
        self.db = SupabaseService()

    def compute_gaps(self, user_id: str) -> list[dict]:
        user_skills = self.db.get_user_skills(user_id)
        profile = self.db.get_profile(user_id)
        if not profile:
            return []

        # Build current skill map (name -> {level, confidence})
        current_map = {}
        for us in user_skills:
            name = us.get("skill_name", "")
            if name:
                current_map[name.lower()] = {
                    "level": us.get("current_level", "beginner"),
                    "confidence": us.get("confidence", 1),
                }

        # Get target skills from active goal via AI analysis
        goals = self.db.client.table("goals").select("*").eq("user_id", user_id).eq("status", "active").execute()
        if not goals.data:
            return []

        goal = goals.data[0]
        target_skills = []

        # Method 1: Check goal_skills table
        goal_skills = self.db.client.table("goal_skills").select(
            "*, skills(name)"
        ).eq("goal_id", goal["id"]).execute()

        if goal_skills.data:
            for gs in goal_skills.data:
                skill_name = gs.get("skills", {}).get("name", "") if isinstance(gs.get("skills"), dict) else ""
                if skill_name:
                    target_skills.append({
                        "name": skill_name,
                        "required_level": gs.get("required_level", "intermediate"),
                        "importance": gs.get("importance", 0.5),
                    })

        # Method 2: If no goal_skills, extract from the raw goal using AI
        if not target_skills:
            try:
                ai = AIService()
                analysis = ai.analyze_goal(goal["raw_goal"])
                for skill_name in analysis.get("target_skills", []):
                    target_skills.append({
                        "name": skill_name,
                        "required_level": "intermediate",
                        "importance": 0.7,
                    })
                for skill_name in analysis.get("likely_prerequisites", []):
                    target_skills.append({
                        "name": skill_name,
                        "required_level": "intermediate",
                        "importance": 0.5,
                    })
            except Exception:
                pass

        # Compute gaps
        gaps = []
        for ts in target_skills:
            skill_name = ts["name"]
            required_level = ts["required_level"]
            importance = ts["importance"]

            current = current_map.get(skill_name.lower(), {"level": "none", "confidence": 0})
            current_level = current["level"]

            current_num = LEVEL_MAP.get(current_level, 0)
            target_num = LEVEL_MAP.get(required_level, 2)
            gap_num = max(0, target_num - current_num)

            # If user has no record of this skill at all, it's critical
            if current_level == "none":
                gap_label = "critical"
            else:
                gap_label = GAP_LABELS.get(gap_num, "high")

            gaps.append({
                "skill_name": skill_name,
                "skill_id": "",
                "current_level": current_level,
                "target_level": required_level,
                "gap": gap_label,
                "importance": importance,
                "prerequisites": [],
                "recommended_action": self._get_action(gap_num, skill_name, current_level),
            })

        # Sort: critical/high gaps first, then by importance
        gap_order = {"critical": 4, "high": 3, "medium": 2, "low": 1, "none": 0}
        gaps.sort(key=lambda g: (gap_order.get(g["gap"], 0), g["importance"]), reverse=True)
        return gaps

    def _get_action(self, gap: int, skill: str, current_level: str) -> str:
        if current_level == "none":
            return f"Start learning {skill} from scratch — this is a critical skill for your goal"
        if gap == 0:
            return f"You're proficient in {skill} — maintain through practice"
        elif gap == 1:
            return f"Deepen your {skill} knowledge with advanced concepts and projects"
        elif gap == 2:
            return f"Build solid {skill} fundamentals through structured study"
        else:
            return f"Begin learning {skill} with beginner-friendly resources"
