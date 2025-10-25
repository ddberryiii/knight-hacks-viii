from backend.core.gemini_client import ask_gemini
from backend.core.ml_recommender import recommend_anime_by_title


def get_gemini_enhanced_recommendations(favorites: list[str], top_n: int = 5) -> list[dict]:
    """
    Combine ML-based recommendations with Gemini summaries.
    Returns a list of {title, summary}.
    """
    # Get a merged set of model recs for all favorites
    combined_recs = []
    for fav in favorites:
        recs = recommend_anime_by_title(fav, top_n=top_n)
        combined_recs.extend(recs)

    unique_recs = list(dict.fromkeys(combined_recs))[:top_n]

    # Ask Gemini to explain each
    results = []
    for anime in unique_recs:
        prompt = (
            f"The user enjoys these anime: {', '.join(favorites)}.\n"
            f"Explain in 2-3 sentences why they might also enjoy '{anime}', "
            f"and mention themes, tone, or characters that overlap."
        )
        try:
            explanation = ask_gemini(prompt)
            results.append({"title": anime, "summary": explanation.strip()})
        except Exception as e:
            results.append({"title": anime, "summary": f"Error calling Gemini: {e}"})

    return results
