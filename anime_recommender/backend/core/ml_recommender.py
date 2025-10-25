import os
import pandas as pd
from rapidfuzz import fuzz
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

# Navigate four levels up to reach the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_PATH = os.path.join(BASE_DIR, "data", "cleaned_data.parquet")

print("Loading dataset from:", DATA_PATH)
df = pd.read_parquet(DATA_PATH)

for col in ['genres', 'themes', 'demographics', 'synopsis', 'studios', 'type', 'rating']:
    df[col] = df[col].astype(str)

# TF-IDF encoders
vectorizer_genres = TfidfVectorizer(stop_words='english')
vectorizer_themes = TfidfVectorizer(stop_words='english')
vectorizer_synopsis = TfidfVectorizer(stop_words='english', max_features=10000)
vectorizer_studios = TfidfVectorizer(stop_words='english')

# Transform each feature
tfidf_genres = normalize(vectorizer_genres.fit_transform(df['genres']))
tfidf_themes = normalize(vectorizer_themes.fit_transform(df['themes']))
tfidf_synopsis = normalize(vectorizer_synopsis.fit_transform(df['synopsis']))
tfidf_studios = normalize(vectorizer_studios.fit_transform(df['studios']))

# Combine with weights
combined_matrix = hstack([
    2.0 * tfidf_genres,
    1.5 * tfidf_themes,
    1.0 * tfidf_synopsis,
    0.5 * tfidf_studios
])

cosine_sim = cosine_similarity(combined_matrix, combined_matrix)
print("✅ Model loaded and cosine similarity matrix computed.")


def recommend_anime_by_title(title: str, top_n: int = 5):
    """Return top-N similar anime for a given title string."""
    matches = df[df['name'].str.lower() == title.lower()]
    if matches.empty:
        return []

    idx = matches.index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1: top_n + 6]

    recs = []
    for i, _ in sim_scores:
        cand_name = df.loc[i, 'name']
        if fuzz.partial_ratio(title.lower(), cand_name.lower()) < 75:
            recs.append(cand_name)
        if len(recs) >= top_n:
            break

    return recs
