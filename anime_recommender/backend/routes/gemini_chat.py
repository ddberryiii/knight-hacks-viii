from fastapi import APIRouter, HTTPException
from backend.core.gemini_client import ask_gemini

router = APIRouter()

@router.post("/chat")
def chat_with_gemini(prompt: str):
    try:
        response = ask_gemini(prompt)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
