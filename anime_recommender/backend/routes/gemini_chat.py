from fastapi import APIRouter, HTTPException
from backend.core.gemini_client import ask_gemini

router = APIRouter()

# Store simple in-memory chat history (could later connect to a DB)
chat_sessions = {}

@router.post("/chat/")
def chat_with_gemini(user_id: str, message: str):
    """Allow user to chat with Gemini about anime or recommendations."""
    if user_id not in chat_sessions:
        chat_sessions[user_id] = []

    # Maintain conversational context
    history = chat_sessions[user_id]
    prompt = "\n".join(history + [message])

    try:
        response = ask_gemini(prompt)
        chat_sessions[user_id].append(f"User: {message}")
        chat_sessions[user_id].append(f"Gemini: {response}")
        return {"reply": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
