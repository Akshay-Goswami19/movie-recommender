import os
import pickle
import numpy as np
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

app = FastAPI(title="Movie Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Load models at startup ----------
print("Loading models...")
with open("df.pkl", "rb") as f:
    df = pickle.load(f)
with open("indices.pkl", "rb") as f:
    indices = pickle.load(f)
with open("tfidf_matrix.pkl", "rb") as f:
    tfidf_matrix = pickle.load(f)
print(f"Loaded {len(df)} movies.")


# ---------- Helpers ----------
async def fetch_tmdb_poster(title: str) -> str | None:
    if not TMDB_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(
                f"{TMDB_BASE}/search/movie",
                params={"api_key": TMDB_API_KEY, "query": title},
            )
            results = r.json().get("results", [])
            if results and results[0].get("poster_path"):
                return TMDB_IMG + results[0]["poster_path"]
    except Exception:
        pass
    return None


def get_recommendations(title: str, n: int = 10) -> list[dict]:
    if title not in indices:
        return []
    idx = indices[title]
    scores = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    top_indices = np.argsort(scores)[::-1][1: n + 1]
    results = []
    for i in top_indices:
        row = df.iloc[i]
        results.append({
            "title": row["title"],
            "overview": row.get("overview", ""),
            "genres": row.get("genres", ""),
            "vote_average": float(row.get("vote_average", 0)),
            "popularity": float(row.get("popularity", 0)),
            "poster_url": None,  # filled async by endpoint
        })
    return results


# ---------- Endpoints ----------
@app.get("/")
def root():
    return {"message": "Movie Recommender API is running"}


@app.get("/movies/search")
def search_movies(q: str = Query(..., min_length=1)):
    """Return movie titles matching the query (for autocomplete)."""
    q_lower = q.lower()
    matches = [t for t in indices.index if q_lower in t.lower()][:20]
    return {"results": matches}


@app.get("/movies/recommend")
async def recommend(title: str = Query(...), n: int = Query(10, ge=1, le=20)):
    """Return top-n recommendations for a given movie title."""
    if title not in indices:
        raise HTTPException(status_code=404, detail=f"Movie '{title}' not found.")

    recs = get_recommendations(title, n)

    # Fetch posters concurrently
    async with httpx.AsyncClient(timeout=5) as client:
        async def get_poster(movie_title):
            if not TMDB_API_KEY:
                return None
            try:
                r = await client.get(
                    f"{TMDB_BASE}/search/movie",
                    params={"api_key": TMDB_API_KEY, "query": movie_title},
                )
                results = r.json().get("results", [])
                if results and results[0].get("poster_path"):
                    return TMDB_IMG + results[0]["poster_path"]
            except Exception:
                pass
            return None

        import asyncio
        posters = await asyncio.gather(*[get_poster(m["title"]) for m in recs])

    for movie, poster in zip(recs, posters):
        movie["poster_url"] = poster

    return {"query": title, "recommendations": recs}


@app.get("/movies/info")
async def movie_info(title: str = Query(...)):
    """Return info + poster for a single movie."""
    if title not in indices:
        raise HTTPException(status_code=404, detail=f"Movie '{title}' not found.")
    idx = indices[title]
    row = df.iloc[idx]
    poster = await fetch_tmdb_poster(title)
    return {
        "title": row["title"],
        "overview": row.get("overview", ""),
        "genres": row.get("genres", ""),
        "vote_average": float(row.get("vote_average", 0)),
        "popularity": float(row.get("popularity", 0)),
        "poster_url": poster,
    }