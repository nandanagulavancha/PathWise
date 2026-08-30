from app.services.supabase_service import SupabaseService
from app.services.ai_service import AIService
from app.models.schemas import FeedbackCreate


class AdaptiveEngine:
    def __init__(self):
        self.db = SupabaseService()
        self.ai = AIService()

    def adapt(self, path_id: str) -> dict:
        # Get path with segments
        result = self.db.client.table("learning_paths").select(
            "*, learning_segments(*)"
        ).eq("id", path_id).single().execute()

        if not result.data:
            return {"error": "Path not found"}

        path = result.data
        user_id = path["user_id"]
        segments = sorted(path.get("learning_segments", []), key=lambda s: s.get("sequence", 0))

        # Check quiz performance for current segments
        adaptations = []
        for segment in segments:
            if segment.get("status") != "in_progress":
                continue

            # Get quiz attempts for this segment
            quizzes = self.db.client.table("quizzes").select(
                "id"
            ).eq("segment_id", segment["id"]).execute()

            if not quizzes.data:
                continue

            for quiz in quizzes.data:
                attempts = self.db.client.table("quiz_attempts").select("*").eq(
                    "quiz_id", quiz["id"]
                ).eq("user_id", user_id).order("completed_at", desc=True).limit(1).execute()

                if attempts.data:
                    latest = attempts.data[0]
                    score = latest.get("score", 0)

                    if score < 0.5:
                        adaptations.append({
                            "type": "add_review",
                            "segment_id": segment["id"],
                            "reason": f"Quiz score ({score:.0%}) below threshold. Adding review material.",
                        })
                        self.db.update_segment_status(segment["id"], "needs_review")
                    elif score >= 0.8:
                        adaptations.append({
                            "type": "advance",
                            "segment_id": segment["id"],
                            "reason": f"Excellent quiz score ({score:.0%}). Unlocking next segment.",
                        })
                        self.db.update_segment_status(segment["id"], "completed")
                        # Unlock next
                        next_seq = segment.get("sequence", 0) + 1
                        for s in segments:
                            if s.get("sequence") == next_seq and s.get("status") == "locked":
                                self.db.update_segment_status(s["id"], "in_progress")
                                break

        return {"adaptations": adaptations, "path_id": path_id}

    def process_feedback(self, user_id: str, feedback: FeedbackCreate):
        if feedback.type == "too_easy" and feedback.segment_id:
            self.db.update_segment_status(feedback.segment_id, "completed")
        elif feedback.type == "too_difficult" and feedback.segment_id:
            self.db.update_segment_status(feedback.segment_id, "needs_review")
        elif feedback.type == "already_know" and feedback.segment_id:
            self.db.update_segment_status(feedback.segment_id, "completed")
