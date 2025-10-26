# recommender_knn.py
from __future__ import annotations
from typing import List, Dict, Optional
import numpy as np
import pandas as pd
import math

# Direct import since animeknn.py is in the same folder
import animeknn


def _build_id_index_map(metadata: pd.DataFrame) -> Dict[int, int]:
    """Create a mapping from anime_id → dataframe index."""
    ids = pd.to_numeric(metadata.get("anime_id"), errors="coerce")
    return {int(aid): idx for idx, aid in ids.dropna().items()}

def clean_json_value(value):
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if pd.isna(value):
        return None
    return value


_ID_TO_IDX = _build_id_index_map(animeknn.metadata)


class AnimeKNNRecommender:
    """
    Adapter class to use animeknn inside Flask.
    Methods:
      - search(q)
      - recommend(anime_ids)
    """

    def __init__(self):
        self.embeddings = animeknn.embeddings
        self.metadata = animeknn.metadata
        self.raw_data = animeknn.raw_data
        self.default_candidates = getattr(animeknn, "DEFAULT_CANDIDATES", 100)

    # -------------------- SEARCH --------------------

    def search(self, q: str, limit: int = 10) -> List[Dict]:
        if not q:
            return []

        q_lower = q.lower()

        # --- We'll search directly in raw_data ---
        cols = [
            c for c in ["english_name", "name"]
            if c in self.raw_data.columns
        ]
        if not cols:
            return []

        # --- Build mask: look for the query in any name column ---
        mask = False
        for c in cols:
            mask = mask | self.raw_data[c].astype(str).str.lower().str.contains(q_lower, na=False)

        hits = self.raw_data[mask].head(limit)

        # --- Helper to sanitize bad strings ---
        def safe_str(value, fallback="Unknown"):
            if pd.isna(value) or value is None:
                return fallback
            s = str(value).strip()
            return fallback if not s or s.lower() == "nan" else s

        # --- Build results ---
        results = []
        for _, row in hits.iterrows():
            anime_id = int(row.get("anime_id", -1))
            if anime_id == -1:
                continue

            # Prefer English name if available
            display_name = row.get("english_name") or row.get("name")
            clean_name = safe_str(display_name)

            results.append({
                "anime_id": anime_id,
                "name": clean_name,
                "image_url": safe_str(row.get("image_url"), None)
            })

        return results

    # ----------------- RECOMMENDATIONS -----------------

    def recommend(self, anime_ids: List[int], k: int = 20, lambda_mult: float = 0.7) -> List[Dict]:
        if not anime_ids:
            return []

        # Resolve first valid id
        query_idx = next((_ID_TO_IDX[aid] for aid in anime_ids if aid in _ID_TO_IDX), None)
        if query_idx is None:
            return []

        query_vec = self.embeddings[query_idx]

        # 1) Get candidate pool
        cand_indices, _ = animeknn.knn_search(
            query_vec, self.embeddings,
            k=self.default_candidates,
            exclude_idx=query_idx
        )

        # 2) Filter same-series results
        cand_indices = animeknn.filter_same_series(cand_indices, query_idx, self.metadata)
        if not len(cand_indices):
            cand_indices, _ = animeknn.knn_search(query_vec, self.embeddings, k=k, exclude_idx=query_idx)

        # 3) Re-rank using MMR (diversity)
        if len(cand_indices) > k:
            cand_emb = self.embeddings[cand_indices]
            order = animeknn.mmr_rerank(cand_emb, query_vec, lambda_mult=lambda_mult, top_n=k * 3)
            cand_indices = cand_indices[order]

        # 4) Genre diversity
        cand_indices = animeknn.diversify_by_genre(cand_indices[:k * 2], self.metadata, max_per_genre=20)

        # 5) Build response objects
        results = []
        for idx in cand_indices[:k]:
            meta = self.metadata.iloc[idx]
            aid = int(meta.get("anime_id"))
            sim = float(animeknn.cosine_similarity_batch(query_vec, self.embeddings[idx:idx + 1])[0])

            # Prefer info from raw_data
            r = self.raw_data[self.raw_data["anime_id"] == aid]
            if not r.empty:
                row = r.iloc[0]
                name = row.get("name", meta.get("name", "Unknown"))
                score = row.get("score", meta.get("score", "N/A"))
                episodes = row.get("episodes", meta.get("episodes", "N/A"))
                genres = row.get("genres", meta.get("genres", "N/A"))
                image_url = row.get("image_url") if "image_url" in r.columns else None
                anime_url = row.get("anime_url") if "anime_url" in r.columns else None
            else:
                name = meta.get("name", "Unknown")
                score = meta.get("score", "N/A")
                episodes = meta.get("episodes", "N/A")
                genres = meta.get("genres", "N/A")
                image_url = anime_url = None

            results.append({
                "anime_id": clean_json_value(aid),
                "name": clean_json_value(name),
                "similarity": clean_json_value(sim),
                "score": clean_json_value(score),
                "episodes": clean_json_value(episodes),
                "genres": clean_json_value(genres),
                "image_url": clean_json_value(image_url),
                "anime_url": clean_json_value(anime_url),
            })

        return results