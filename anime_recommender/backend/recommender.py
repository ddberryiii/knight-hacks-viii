import pandas as pd
import re
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
from scipy.sparse import hstack

class AnimeRecommender:
    def __init__(self, data_dir="./data"):
        print("🔄 Loading anime dataset...")
        self.df = self._load_data(data_dir)
        self._prepare_vectors()
        print("✅ Recommender initialized!")

    def _load_data(self, data_dir):
        df = pd.read_parquet(f"{data_dir}/cleaned_data.parquet")
        raw = pd.read_csv(f"{data_dir}/raw_data.csv", usecols=["anime_id", "anime_url", "image_url", "name"])
        df = df.merge(raw, on="anime_id", how="left", suffixes=('_old', ''))
        if "name_old" in df.columns:
            df.drop(columns=["name_old"], inplace=True)
        return df

    def _prepare_vectors(self):
        for col in ["genres", "themes", "synopsis", "studios"]:
            self.df[col] = self.df[col].astype(str)

        print("⚙️ Computing TF-IDF features...")
        vec = lambda c, maxf=None: normalize(TfidfVectorizer(stop_words="english", max_features=maxf).fit_transform(self.df[c]))
        tfidf_genres = vec("genres")
        tfidf_themes = vec("themes")
        tfidf_synopsis = vec("synopsis", maxf=10000)
        tfidf_studios = vec("studios")

        W_GENRES, W_THEMES, W_SYNOPSIS, W_STUDIOS = 2.0, 1.5, 1.0, 0.5
        self.combined = hstack([
            W_GENRES * tfidf_genres,
            W_THEMES * tfidf_themes,
            W_SYNOPSIS * tfidf_synopsis,
            W_STUDIOS * tfidf_studios,
        ])

        self.df["core_name"] = self.df["name"].apply(self._core_name)
        self.cosine_sim = cosine_similarity(self.combined, self.combined)

    def _core_name(self, title):
        if pd.isna(title): return ""
        title = title.lower()
        title = re.split(r'[:\-—–\(\)\[\]]', title)[0]
        title = re.sub(r'\b(season|part|movie|ova|special|remake|final)\b', '', title)
        title = re.sub(r'\b\d+\b', '', title)
        return re.sub(r'\s+', ' ', title).strip()

    def search(self, query):
        if not query: return []
        q = query.lower()
        results = self.df[self.df['name'].str.lower().str.contains(q, na=False)][['anime_id', 'name']].head(15)
        return results.to_dict('records')

    def recommend(self, anime_ids, top_n=10):
        recs = []
        for anime_id in anime_ids:
            if anime_id not in self.df['anime_id'].values:
                continue
            idx = self.df.index[self.df['anime_id'] == anime_id][0]
            scores = list(enumerate(self.cosine_sim[idx]))
            scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
            for i, _ in scores:
                recs.append(self.df.iloc[i][['anime_id', 'name', 'anime_url', 'image_url']].to_dict())
        return recs
