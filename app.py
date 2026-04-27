import streamlit as st
import requests

API_URL = "http://localhost:8000"

# ---------- Page config ----------
st.set_page_config(
    page_title="CineMatch",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- CSS ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: #0a0a0f;
    color: #e8e8f0;
}

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Hero */
.hero {
    text-align: center;
    padding: 3.5rem 0 2rem;
}
.hero h1 {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 5rem;
    letter-spacing: 0.15em;
    background: linear-gradient(135deg, #e50914 0%, #ff6b35 60%, #ffd700 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1;
}
.hero p {
    color: #888;
    font-size: 1rem;
    letter-spacing: 0.05em;
    margin-top: 0.5rem;
}

/* Search bar */
.stTextInput > div > div > input {
    background: #16161f !important;
    border: 1.5px solid #2a2a3a !important;
    border-radius: 12px !important;
    color: #e8e8f0 !important;
    font-size: 1rem !important;
    padding: 0.75rem 1.2rem !important;
    transition: border-color 0.2s;
}
.stTextInput > div > div > input:focus {
    border-color: #e50914 !important;
    box-shadow: 0 0 0 3px rgba(229,9,20,0.15) !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: #16161f !important;
    border: 1.5px solid #2a2a3a !important;
    border-radius: 12px !important;
    color: #e8e8f0 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #e50914, #c0000f) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 2rem !important;
    letter-spacing: 0.04em !important;
    transition: opacity 0.2s, transform 0.15s !important;
    width: 100%;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* Movie card */
.movie-card {
    background: #13131a;
    border: 1px solid #1f1f2e;
    border-radius: 14px;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
    height: 100%;
}
.movie-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(229,9,20,0.2);
    border-color: #e50914;
}
.card-poster {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
    background: #1a1a27;
    display: block;
}
.card-body {
    padding: 0.9rem 1rem;
}
.card-title {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.92rem;
    color: #f0f0f8;
    margin: 0 0 0.4rem;
    line-height: 1.3;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.card-genres {
    font-size: 0.72rem;
    color: #888;
    margin-bottom: 0.5rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.card-rating {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #ffd700;
}
.no-poster {
    width: 100%;
    aspect-ratio: 2/3;
    background: linear-gradient(160deg, #1a1a2e, #0f0f1a);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
}

/* Selected movie hero card */
.selected-card {
    background: linear-gradient(135deg, #16161f, #0f0f1a);
    border: 1px solid #2a2a3a;
    border-radius: 16px;
    padding: 1.5rem;
    display: flex;
    gap: 1.5rem;
    align-items: flex-start;
    margin-bottom: 2rem;
}
.selected-poster img {
    width: 130px;
    border-radius: 10px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.5);
}
.selected-poster .no-poster-sm {
    width: 130px;
    height: 195px;
    border-radius: 10px;
    background: #1a1a2e;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.5rem;
}
.selected-info h2 {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2rem;
    letter-spacing: 0.08em;
    color: #f0f0f8;
    margin: 0 0 0.3rem;
}
.selected-info .genres-badge {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 0.7rem;
}
.genre-tag {
    background: rgba(229,9,20,0.15);
    color: #e50914;
    border: 1px solid rgba(229,9,20,0.3);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.72rem;
    font-weight: 500;
}
.selected-info .overview {
    color: #aaa;
    font-size: 0.88rem;
    line-height: 1.6;
    margin-top: 0.5rem;
    max-width: 600px;
}
.rating-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.5rem;
}
.rating-big {
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffd700;
}

/* Section title */
.section-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem;
    letter-spacing: 0.1em;
    color: #e8e8f0;
    margin: 1.5rem 0 1rem;
    padding-left: 2px;
}

/* Spinner */
.stSpinner > div { border-top-color: #e50914 !important; }

/* Slider */
.stSlider > div { color: #888 !important; }
</style>
""", unsafe_allow_html=True)


# ---------- Helpers ----------
def search_movies(query: str):
    try:
        r = requests.get(f"{API_URL}/movies/search", params={"q": query}, timeout=5)
        return r.json().get("results", [])
    except Exception:
        return []


def get_movie_info(title: str):
    try:
        r = requests.get(f"{API_URL}/movies/info", params={"title": title}, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def get_recommendations(title: str, n: int):
    try:
        r = requests.get(
            f"{API_URL}/movies/recommend",
            params={"title": title, "n": n},
            timeout=15,
        )
        if r.status_code == 200:
            return r.json().get("recommendations", [])
    except Exception:
        pass
    return []


def render_movie_card(movie: dict):
    poster = movie.get("poster_url")
    title = movie.get("title", "Unknown")
    genres = movie.get("genres", "")
    rating = movie.get("vote_average", 0)

    if poster:
        poster_html = f'<img src="{poster}" class="card-poster" alt="{title}">'
    else:
        poster_html = '<div class="no-poster">🎬</div>'

    stars = "★" * round(rating / 2) if rating else ""

    return f"""
    <div class="movie-card">
        {poster_html}
        <div class="card-body">
            <div class="card-title" title="{title}">{title}</div>
            <div class="card-genres">{genres[:40] if genres else "—"}</div>
            <div class="card-rating">⭐ {rating:.1f} {stars}</div>
        </div>
    </div>
    """


# ---------- App ----------
# Hero
st.markdown("""
<div class="hero">
    <h1>CINEMATCH</h1>
    <p>Your AI-powered movie recommendation engine</p>
</div>
""", unsafe_allow_html=True)

# Search row
col1, col2, col3 = st.columns([5, 2, 1])

with col1:
    search_query = st.text_input(
        "search",
        placeholder="🔍  Search for a movie (e.g. The Dark Knight)...",
        label_visibility="collapsed",
        key="search_input",
    )

with col2:
    num_recs = st.slider("Recommendations", 5, 20, 10, label_visibility="collapsed")

# Autocomplete / selection
selected_title = None

if search_query and len(search_query) >= 2:
    suggestions = search_movies(search_query)
    if suggestions:
        selected_title = st.selectbox(
            "Select a movie",
            options=suggestions,
            label_visibility="collapsed",
        )
    else:
        st.markdown('<p style="color:#666;font-size:0.85rem;padding:0.3rem 0;">No movies found. Try a different search.</p>', unsafe_allow_html=True)

# Recommend button
with col3:
    go = st.button("GO", use_container_width=True)

st.markdown("---")

# ---------- Results ----------
if selected_title and go:
    # Selected movie info
    with st.spinner("Fetching movie details..."):
        info = get_movie_info(selected_title)

    if info:
        poster_html = (
            f'<img src="{info["poster_url"]}" style="width:130px;border-radius:10px;box-shadow:0 8px 30px rgba(0,0,0,0.5);">'
            if info.get("poster_url")
            else '<div class="no-poster-sm">🎬</div>'
        )
        genres = info.get("genres", "")
        genre_tags = " ".join(
            f'<span class="genre-tag">{g.strip()}</span>'
            for g in genres.split() if g.strip()
        ) if genres else ""

        overview = info.get("overview", "No overview available.")
        rating = info.get("vote_average", 0)

        st.markdown(f"""
        <div class="selected-card">
            <div class="selected-poster">{poster_html}</div>
            <div class="selected-info">
                <h2>{info['title']}</h2>
                <div class="genres-badge">{genre_tags}</div>
                <div class="rating-row">
                    <span class="rating-big">⭐ {rating:.1f} / 10</span>
                </div>
                <div class="overview">{overview[:300]}{"..." if len(overview) > 300 else ""}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Recommendations
    st.markdown(f'<div class="section-title">Because you like {selected_title}</div>', unsafe_allow_html=True)

    with st.spinner("Finding recommendations..."):
        recs = get_recommendations(selected_title, num_recs)

    if recs:
        cols_per_row = 5
        for row_start in range(0, len(recs), cols_per_row):
            cols = st.columns(cols_per_row)
            for col, movie in zip(cols, recs[row_start: row_start + cols_per_row]):
                with col:
                    st.markdown(render_movie_card(movie), unsafe_allow_html=True)
    else:
        st.warning("No recommendations found.")

elif not search_query:
    # Landing state
    st.markdown("""
    <div style="text-align:center; padding: 3rem 0; color: #444;">
        <div style="font-size:4rem; margin-bottom:1rem;">🎬</div>
        <p style="font-size:1.1rem; color:#555;">Search for any movie above to discover similar films</p>
        <p style="font-size:0.85rem; color:#333; margin-top:0.5rem;">42,000+ movies in the database</p>
    </div>
    """, unsafe_allow_html=True)