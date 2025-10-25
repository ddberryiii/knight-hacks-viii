from fastapi import APIRouter
from backend.core.recommender import get_gemini_enhanced_recommendations

router = APIRouter()

@router.post("/")
def recommend_anime(favorites: list[str]):
    results = get_gemini_enhanced_recommendations(favorites)
    return {"recommendations": results}
