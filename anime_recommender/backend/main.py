from fastapi import FastAPI
from backend.routes import gemini_chat, recommend

app = FastAPI(title="Anime Recommender API")

app.include_router(gemini_chat.router, prefix="/api/gemini")
app.include_router(recommend.router, prefix="/api/recommend")
@app.get("/")
def root():
    return {"message": "Anime Recommender API running"}
