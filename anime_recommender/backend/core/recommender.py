from backend.core.gemini_client import ask_gemini

# Example static fallback dataset (for local testing)
ANIME_DB = [
    "Attack on Titan", "Naruto", "One Piece", "Jujutsu Kaisen", "Demon Slayer",
    "Fullmetal Alchemist: Brotherhood", "Death Note", "My Hero Academia", "Bleach",
    "Tokyo Ghoul", "Vinland Saga", "Chainsaw Man", "Hunter x Hunter"
]


def get_recommendations(favorites: list[str], use_gemini: bool = True) -> dict:
    """
    Given a list of the user's favorite anime titles, return top recommendations.
    Optionally uses Gemini to elaborate on why each recommendation fits.
    """
    recs = []
    for anime_title in ANIME_DB:
        if anime_title not in favorites:
            score = sum(
                fav.lower() in anime_title.lower() or anime_title.lower() in fav.lower()
                for fav in favorites
            )
            recs.append((anime_title, score))

    top_recs = [anime for anime, _ in sorted(recs, key=lambda x: x[1], reverse=True)[:5]]

    if use_gemini:
        detailed_recs = {}
        for anime in top_recs:
            prompt = (
                f"The user enjoys these anime: {', '.join(favorites)}.\n"
                f"Explain in 2-3 sentences why they might also enjoy '{anime}', "
                f"and what themes, characters, or tone it shares."
            )
            try:
                response_text = ask_gemini(prompt)
                detailed_recs[anime] = response_text.strip()
            except Exception as e:
                detailed_recs[anime] = f"(Error getting summary: {e})"
        return detailed_recs

    return {anime: "No summary (Gemini disabled)" for anime in top_recs}



if __name__ == "__main__":
    # Quick local test
    test_favorites = ["Attack on Titan", "Naruto", "Jujutsu Kaisen"]
    results = get_recommendations(test_favorites)
    print("\nSample Recommendations:\n")
    for title, summary in results.items():
        print(f"🎬 {title} → {summary}\n")
