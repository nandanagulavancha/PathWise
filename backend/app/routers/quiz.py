from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.schemas import QuizGenerateRequest, QuizSubmitRequest, QuizResult
from app.services.quiz_engine import QuizEngine
from app.services.ai_service import AIService

router = APIRouter()


class QuickQuizRequest(BaseModel):
    resource_title: str
    segment_id: str


@router.post("/quick")
def quick_quiz(data: QuickQuizRequest):
    ai = AIService()
    try:
        questions = ai.generate_quiz(
            data.resource_title,
            [data.resource_title],
            [data.resource_title],
        )
        if questions:
            q = questions[0]
            return {
                "question": q["question"],
                "options": q["options"],
                "correct_answer": q["correct_answer"],
                "explanation": q.get("explanation", ""),
            }
        return {"question": None}
    except Exception as e:
        print(f"Quick quiz error: {e}")
        return {"question": None}


@router.post("/generate")
def generate_quiz(data: QuizGenerateRequest):
    engine = QuizEngine()
    try:
        quiz = engine.generate(data.segment_id)
        return quiz
    except Exception as e:
        print(f"Quiz generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit")
def submit_quiz(data: QuizSubmitRequest, user_id: str = ""):
    engine = QuizEngine()
    try:
        result = engine.evaluate(data.quiz_id, data.answers, user_id)
        return result
    except Exception as e:
        print(f"Quiz submit error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{user_id}")
def quiz_history(user_id: str):
    from app.services.supabase_service import SupabaseService
    db = SupabaseService()
    history = db.get_quiz_attempts(user_id)
    return history
