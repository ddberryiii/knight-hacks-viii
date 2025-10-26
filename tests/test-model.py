import pandas as pd
import numpy as np
import re
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
from scipy.sparse import hstack

df = pd.read_parquet("../anime_recommender/backend/data/cleaned_data.parquet")

for col in ['genres', 'themes', 'demographics', 'synopsis', 'studios', 'type', 'rating']:
    df[col] = df[col].astype(str)

vectorizer_genres = TfidfVectorizer(stop_words='english')
vectorizer_themes = TfidfVectorizer(stop_words='english')
vectorizer_synopsis = TfidfVectorizer(stop_words='english', max_features=10000)
vectorizer_studios = TfidfVectorizer(stop_words='english')

tfidf_genres = vectorizer_genres.fit_transform(df['genres'])
tfidf_themes = vectorizer_themes.fit_transform(df['themes'])
tfidf_synopsis = vectorizer_synopsis.fit_transform(df['synopsis'])
tfidf_studios = vectorizer_studios.fit_transform(df['studios'])

tfidf_genres = normalize(tfidf_genres)
tfidf_themes = normalize(tfidf_themes)
tfidf_synopsis = normalize(tfidf_synopsis)
tfidf_studios = normalize(tfidf_studios)

W_GENRES = 2.0
W_THEMES = 1.5
W_SYNOPSIS = 1.0
W_STUDIOS = 0.5

combined_matrix = hstack([
    W_GENRES * tfidf_genres,
    W_THEMES * tfidf_themes,
    W_SYNOPSIS * tfidf_synopsis,
    W_STUDIOS * tfidf_studios
])

def extract_core_name(title: str) -> str:
    if pd.isna(title):
        return ''
    title = title.lower()
    title = re.split(r'[:\-–—\(\)\[\]]', title)[0]
    title = re.sub(
        r'\b(season|part|special|movie|ova|final|chapter|edition|arc|remake|rebuild|stage|act|sequel|prequel|series)\b',
        '', title
    )
    title = re.sub(r'\b(\d+(st|nd|rd|th))\b', '', title)
    title = re.sub(r'\b(\d+|i{1,3}|iv|v|vi{0,3}|vii{0,3}|ix|x)\b', '', title)
    title = re.sub(r'(no|by|kizuna|link|divide|zero|hyouketsu)', '', title)
    title = re.sub(r'[^a-z0-9\s]', ' ', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title

df["core_name"] = df["name"].apply(extract_core_name)

cosine_sim = cosine_similarity(combined_matrix, combined_matrix)
print("Combined TF-IDF matrix and cosine similarity computed.")

def recommend_anime_by_id(anime_id, top_n=5):
    if anime_id not in df['anime_id'].values:
        return f"No anime found with id {anime_id}."

    idx = df.index[df['anime_id'] == anime_id][0]
    base_name = df.loc[idx, 'name']
    base_core = df.loc[idx, 'core_name']

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    recs = []
    for i, _ in sim_scores:
        if i == idx:
            continue

        cand_core = df.loc[i, 'core_name']
        cand_name = df.loc[i, 'name']

        if cand_core == base_core:
            continue
        if base_core in cand_core or cand_core in base_core:
            continue
        if fuzz.partial_ratio(base_core, cand_core) > 75:
            continue
        if re.search(r'(season|part|ova|special|movie|final|rebuild)', cand_name, re.I):
            if base_core.split()[0] in cand_core:
                continue

        recs.append(i)
        if len(recs) >= top_n * 3:
            break

    results = df.iloc[recs][['anime_id', 'name', 'core_name', 'score', 'genres', 'rating']]
    results = results.drop_duplicates(subset='core_name', keep='first').head(top_n)
    return results[['anime_id', 'name', 'score']].reset_index(drop=True)

print(recommend_anime_by_id(9253, top_n=5))