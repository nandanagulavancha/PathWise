from app.services.supabase_service import SupabaseService
from app.services.ai_service import AIService


class QuizEngine:
    def __init__(self):
        self.db = SupabaseService()
        self.ai = AIService()

    async def generate(self, segment_id: str) -> dict:
        # Get segment info
        result = self.db.client.table("learning_segments").select(
            "*, segment_resources(resources(title))"
        ).eq("id", segment_id).single().execute()

        if not result.data:
            return {"error": "Segment not found"}

        segment = result.data
        skills = segment.get("skills", [segment.get("title", "")])
        resource_titles = [
            r.get("resources", {}).get("title", "")
            for r in segment.get("segment_resources", [])
            if r.get("resources")
        ]

        # Generate quiz questions
        questions = await self.ai.generate_quiz(
            segment.get("title", ""),
            skills if isinstance(skills, list) else [skills],
            resource_titles,
        )

        if not questions:
            return {"error": "Failed to generate quiz"}

        # Save quiz
        quiz_data = {"segment_id": segment_id, "title": f"Reflection: {segment.get('title', '')}"}
        quiz = await self.db.save_quiz(quiz_data)
        quiz_id = quiz.get("id", "temp")

        # Save questions
        saved_questions = []
        for q in questions:
            q_data = {
                "quiz_id": quiz_id,
                "question": q["question"],
                "options": q["options"],
                "correct_answer": q["correct_answer"],
                "explanation": q.get("explanation", ""),
                "skill_id": None,
                "difficulty": q.get("difficulty", "medium"),
            }
            saved_questions.append(q_data)

        if saved_questions:
            await self.db.save_quiz_questions(saved_questions)

        return {
            "quiz_id": quiz_id,
            "title": quiz_data["title"],
            "questions": [
                {
                    "id": str(i),
                    "question": q["question"],
                    "options": q["options"],
                    "skill_tested": q.get("skill_tested", ""),
                    "difficulty": q.get("difficulty", "medium"),
                }
                for i, q in enumerate(questions)
            ],
        }

    async def evaluate(self, quiz_id: str, answers: list[int], user_id: str = "") -> dict:
        quiz = await self.db.get_quiz(quiz_id)
        if not quiz:
            return {"error": "Quiz not found"}

        questions = quiz.get("quiz_questions", [])
        if not questions:
            return {"error": "No questions found"}

        correct = 0
        for i, (q, a) in enumerate(zip(questions, answers)):
            if a == q.get("correct_answer"):
                correct += 1

        score = correct / max(len(questions), 1)

        # Analyze result
        analysis = await self.ai.analyze_quiz_result(score, questions, answers, {})

        # Save attempt if user_id is valid
        if user_id and len(user_id) > 10:
            try:
                attempt_data = {
                    "quiz_id": quiz_id,
                    "user_id": user_id,
                    "score": score,
                    "answers": answers,
                }
                await self.db.save_quiz_attempt(attempt_data)
            except Exception as e:
                print(f"Failed to save quiz attempt: {e}")

        return {
            "quiz_id": quiz_id,
            "score": score,
            "total_questions": len(questions),
            "correct_answers": correct,
            "weak_concepts": analysis.get("weak_concepts", []),
            "strong_concepts": analysis.get("strong_concepts", []),
            "recommended_action": analysis.get("recommended_action", ""),
            "details": [
                {
                    "question": q.get("question", ""),
                    "your_answer": answers[i] if i < len(answers) else -1,
                    "correct_answer": q.get("correct_answer"),
                    "correct": answers[i] == q.get("correct_answer") if i < len(answers) else False,
                    "explanation": q.get("explanation", ""),
                }
                for i, q in enumerate(questions)
            ],
        }
