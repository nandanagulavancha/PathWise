from app.config import get_settings
from supabase import create_client, Client


class SupabaseService:
    def __init__(self):
        settings = get_settings()
        self.client: Client = create_client(settings.supabase_url, settings.supabase_service_role_key)

    def create_profile(self, user_id: str, profile_data) -> dict:
        data = {
            "user_id": user_id,
            "name": profile_data.name,
            "experience_level": profile_data.experience_level,
            "occupation": profile_data.occupation,
            "preferred_language": profile_data.preferred_language,
            "weekly_hours": profile_data.weekly_hours,
            "preferred_learning_style": profile_data.preferred_learning_style,
        }
        result = self.client.table("profiles").upsert(data, on_conflict="user_id").execute()
        return result.data[0] if result.data else data

    def get_profile(self, user_id: str) -> dict | None:
        result = self.client.table("profiles").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None

    def save_interests(self, user_id: str, interests: list[str]):
        for interest in interests:
            interest_result = self.client.table("interests").upsert(
                {"name": interest}, on_conflict="name"
            ).execute()
            if interest_result.data:
                self.client.table("user_interests").upsert(
                    {"user_id": user_id, "interest_id": interest_result.data[0]["id"]},
                    on_conflict="user_id,interest_id"
                ).execute()

    def save_user_skills(self, user_id: str, skills: list):
        for skill_data in skills:
            skill = self.client.table("skills").upsert(
                {"name": skill_data.skill_id, "category": "general"},
                on_conflict="name"
            ).execute()
            if skill.data:
                self.client.table("user_skills").upsert({
                    "user_id": user_id,
                    "skill_id": skill.data[0]["id"],
                    "current_level": skill_data.current_level,
                    "confidence": skill_data.confidence,
                }, on_conflict="user_id,skill_id").execute()

    def create_goal(self, user_id: str, raw_goal: str) -> dict:
        result = self.client.table("goals").insert({
            "user_id": user_id,
            "raw_goal": raw_goal,
            "status": "active",
        }).execute()
        return result.data[0] if result.data else {"id": "temp"}

    def get_skills(self, category: str = None) -> list:
        query = self.client.table("skills").select("*")
        if category:
            query = query.eq("category", category)
        result = query.execute()
        return result.data or []

    def get_skill_prerequisites(self, skill_id: str) -> list:
        result = self.client.table("skill_prerequisites").select(
            "prerequisite_skill_id, skills!skill_prerequisites_prerequisite_skill_id_fkey(name)"
        ).eq("skill_id", skill_id).execute()
        return result.data or []

    def get_user_skills(self, user_id: str) -> list:
        result = self.client.table("user_skills").select(
            "*, skills(name, category)"
        ).eq("user_id", user_id).execute()
        # Flatten the joined skill name
        skills = []
        for item in (result.data or []):
            skill_info = item.get("skills") or {}
            skills.append({
                "skill_id": item.get("skill_id", ""),
                "skill_name": skill_info.get("name", item.get("skill_id", "")),
                "category": skill_info.get("category", ""),
                "current_level": item.get("current_level", "beginner"),
                "confidence": item.get("confidence", 3),
            })
        return skills

    def get_learning_path(self, user_id: str) -> dict | None:
        result = self.client.table("learning_paths").select(
            "*, learning_segments(*, segment_resources(*, resources(*)))"
        ).eq("user_id", user_id).eq("status", "active").order(
            "created_at", desc=True
        ).limit(1).execute()
        if result.data:
            path = result.data[0]
            if path.get("learning_segments"):
                segments = sorted(path.pop("learning_segments"), key=lambda s: s.get("sequence", 0))
                # Flatten segment_resources into resources array
                for seg in segments:
                    sr = seg.pop("segment_resources", []) or []
                    seg["resources"] = [
                        {**item["resources"], "recommendation_score": item.get("recommendation_score"), "recommendation_reason": item.get("recommendation_reason")}
                        for item in sr if item.get("resources")
                    ]
                path["segments"] = segments
            else:
                path["segments"] = []
            return path
        return None

    def save_learning_path(self, path_data: dict) -> dict:
        result = self.client.table("learning_paths").insert(path_data).execute()
        return result.data[0] if result.data else path_data

    def save_learning_segment(self, segment_data: dict) -> dict:
        result = self.client.table("learning_segments").insert(segment_data).execute()
        return result.data[0] if result.data else segment_data

    def save_resource(self, resource_data: dict) -> dict:
        result = self.client.table("resources").upsert(
            resource_data, on_conflict="provider,external_id"
        ).execute()
        return result.data[0] if result.data else resource_data

    def get_resource(self, resource_id: str) -> dict | None:
        result = self.client.table("resources").select("*").eq("id", resource_id).single().execute()
        return result.data

    def save_quiz(self, quiz_data: dict) -> dict:
        result = self.client.table("quizzes").insert(quiz_data).execute()
        return result.data[0] if result.data else quiz_data

    def save_quiz_questions(self, questions: list[dict]):
        self.client.table("quiz_questions").insert(questions).execute()

    def get_quiz(self, quiz_id: str) -> dict | None:
        result = self.client.table("quizzes").select(
            "*, quiz_questions(*)"
        ).eq("id", quiz_id).single().execute()
        return result.data

    def save_quiz_attempt(self, attempt_data: dict) -> dict:
        result = self.client.table("quiz_attempts").insert(attempt_data).execute()
        return result.data[0] if result.data else attempt_data

    def get_quiz_attempts(self, user_id: str) -> list:
        result = self.client.table("quiz_attempts").select("*").eq("user_id", user_id).order("completed_at", desc=True).execute()
        return result.data or []

    def save_feedback(self, user_id: str, feedback_data) -> dict:
        data = {
            "user_id": user_id,
            "resource_id": feedback_data.resource_id,
            "segment_id": feedback_data.segment_id,
            "type": feedback_data.type,
            "text": feedback_data.text,
        }
        result = self.client.table("feedback").insert(data).execute()
        return result.data[0] if result.data else data

    def get_feedback(self, user_id: str) -> list:
        result = self.client.table("feedback").select("*").eq("user_id", user_id).execute()
        return result.data or []

    def get_user_progress(self, user_id: str) -> dict:
        result = self.client.table("progress").select("*").eq("user_id", user_id).execute()
        items = result.data or []
        completed = [i for i in items if i.get("status") == "completed"]
        total_time = sum(i.get("time_spent", 0) for i in items)
        return {
            "overall_percentage": int((len(completed) / max(len(items), 1)) * 100),
            "segments_completed": len(set(i["segment_id"] for i in completed if i.get("segment_id"))),
            "total_segments": len(set(i.get("segment_id") for i in items if i.get("segment_id"))),
            "resources_completed": len(completed),
            "hours_learned": round(total_time / 60, 1),
            "current_streak": 0,
        }

    def mark_progress(self, user_id: str, segment_id: str = None, resource_id: str = None) -> dict:
        data = {"user_id": user_id, "status": "completed", "progress_percentage": 100}
        if segment_id:
            data["segment_id"] = segment_id
        if resource_id:
            data["resource_id"] = resource_id
        result = self.client.table("progress").insert(data).execute()
        return result.data[0] if result.data else data

    def create_conversation(self, user_id: str) -> str:
        result = self.client.table("ai_conversations").insert({
            "user_id": user_id, "title": "New conversation"
        }).execute()
        return result.data[0]["id"] if result.data else "temp"

    def get_conversation_messages(self, conversation_id: str) -> list:
        result = self.client.table("ai_messages").select("*").eq(
            "conversation_id", conversation_id
        ).order("created_at").execute()
        return result.data or []

    def save_message(self, conversation_id: str, role: str, content: str):
        self.client.table("ai_messages").insert({
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
        }).execute()

    def get_conversations(self, user_id: str) -> list:
        result = self.client.table("ai_conversations").select("*").eq(
            "user_id", user_id
        ).order("created_at", desc=True).execute()
        return result.data or []

    def get_goal(self, goal_id: str) -> dict | None:
        result = self.client.table("goals").select("*").eq("id", goal_id).single().execute()
        return result.data

    def update_segment_status(self, segment_id: str, status: str):
        self.client.table("learning_segments").update({"status": status}).eq("id", segment_id).execute()
