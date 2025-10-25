from fastapi import APIRouter
from backend.core.recommender import get_recommendations

router = APIRouter()

@router.post("/")
def recommend_anime(favorites: list[str]):
    recs = get_recommendations(favorites)
    return {"recommendations": recs}
