from fastapi import APIRouter
from app.models.schemas import MentorChatRequest, MentorChatResponse
from app.services.ai_service import AIService
from app.services.supabase_service import SupabaseService

router = APIRouter()


@router.post("/chat")
def chat_with_mentor(user_id: str, data: MentorChatRequest):
    ai = AIService()
    db = SupabaseService()

    # Get user context
    profile = db.get_profile(user_id)
    path = db.get_learning_path(user_id)
    skills = db.get_user_skills(user_id)

    context = {
        "profile": profile,
        "learning_path": path,
        "skills": skills,
    }

    # Get or create conversation
    conversation_id = data.conversation_id
    history = []
    if conversation_id:
        history = db.get_conversation_messages(conversation_id)
    else:
        conversation_id = db.create_conversation(user_id)

    response = ai.chat_with_mentor(data.message, context, history)

    # Save messages
    db.save_message(conversation_id, "user", data.message)
    db.save_message(conversation_id, "assistant", response)

    return MentorChatResponse(response=response, conversation_id=conversation_id)


@router.get("/conversations/{user_id}")
def get_conversations(user_id: str):
    db = SupabaseService()
    conversations = db.get_conversations(user_id)
    return conversations
