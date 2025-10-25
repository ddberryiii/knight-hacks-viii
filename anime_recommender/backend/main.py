from fastapi import FastAPI
from backend.routes import gemini_chat, recommend

app = FastAPI(title="Anime Recommender with Gemini Chat")

app.include_router(recommend.router, prefix="/recommend", tags=["recommendations"])
app.include_router(gemini_chat.router, prefix="/chat", tags=["chat"])

@app.get("/")
def root():
    return {"message": "Anime Recommender + Gemini Chat API running"}
