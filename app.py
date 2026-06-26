import pickle
import random
import pandas as pd
import requests
import streamlit as st
from rapidfuzz import process
from google import genai

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# =========================streamlit
# CUSTOM CSS
# =========================
st.markdown(
    """
<style>
body {
    background-color: #0E1117;
}
.movie-card {
    border-radius: 15px;
    overflow: hidden;
    background-color: #111111;
    margin-bottom: 20px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
    transition: 0.3s;
    height: 100%;
}
.movie-card:hover {
    transform: scale(1.03);
}
.movie-poster {
    width: 100%;
    height: 350px;
    object-fit: cover;
    border-radius: 15px 15px 0px 0px;
}
.movie-content {
    padding: 12px;
}
.movie-title {
    font-size: 16px;
    font-weight: bold;
    color: white;
    margin-bottom: 6px;
}
.movie-rating {
    font-size: 14px;
    color: #ff4b6e;
    margin-bottom: 6px;
}
.movie-genre {
    font-size: 12px;
    color: #cfcfcf;
    margin-bottom: 6px;
}
.match-reasons {
    font-size: 11px;
    color: #a0c4ff;
    margin-top: 6px;
    padding: 5px 8px;
    background-color: rgba(255,255,255,0.05);
    border-radius: 8px;
    border-left: 3px solid #a0c4ff;
}
.stButton>button {
    width: 100%;
    border-radius: 10px;
    background-color: #E50914;
    color: white;
    font-size: 16px;
    height: 3em;
}
.selected-movie-banner {
    padding: 12px 18px;
    background: linear-gradient(90deg, #1a1a2e, #16213e);
    border-left: 4px solid #E50914;
    border-radius: 8px;
    color: white;
    font-size: 16px;
    margin-bottom: 16px;
}
.ai-banner {
    padding: 10px 18px;
    background: linear-gradient(90deg, #0d1b2a, #1b263b);
    border-left: 4px solid #a0c4ff;
    border-radius: 8px;
    color: #a0c4ff;
    font-size: 14px;
    margin-bottom: 16px;
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================
# LOAD SECRETS
# =========================
try:
    API_KEY = st.secrets["TMDB_API_KEY"]
except Exception:
    import os
    API_KEY = os.getenv("TMDB_API_KEY", "")
    if not API_KEY:
        st.error("⚠️ TMDB API key not found. Add it to .streamlit/secrets.toml")
        st.stop()

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    import os
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


# =========================
# DATA INITIALIZATION
# =========================
@st.cache_resource
def load_data():
    movie_list = pickle.load(open("movie_list.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    return movie_list, similarity

movie_list, similarity = load_data()
movies = movie_list["original_title"].values


# =========================
# HELPER FUNCTIONS
# =========================
def fetch_movie_details(movie_id):
    """Fetch live movie details from TMDB API."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        poster_path = data.get("poster_path")
        poster = (
            f"https://image.tmdb.org/t/p/w500/{poster_path}"
            if poster_path
            else "https://via.placeholder.com/500x750?text=No+Poster"
        )

        genres = [genre["name"] for genre in data.get("genres", [])]

        return {
            "poster": poster,
            "rating": round(data.get("vote_average", 0), 1),
            "overview": data.get("overview", "No overview available"),
            "release_date": data.get("release_date", "N/A"),
            "genres": ", ".join(genres) if genres else "N/A",
        }
    except requests.exceptions.RequestException:
        return {
            "poster": "https://upload.wikimedia.org/wikipedia/commons/1/14/No_Image_Available.jpg",
            "rating": "N/A",
            "overview": "Could not fetch details",
            "release_date": "N/A",
            "genres": "N/A",
        }


def get_match_reasons(selected_idx, rec_idx):
    """
    Compare tags between selected movie and recommended movie.
    Returns up to 3 overlapping keywords as match reasons.
    Falls back gracefully if the tags column doesn't exist.
    """
    try:
        selected_tags = set(str(movie_list.iloc[selected_idx].get("tags", "")).lower().split())
        rec_tags = set(str(movie_list.iloc[rec_idx].get("tags", "")).lower().split())
        common = selected_tags & rec_tags
        meaningful = [t for t in common if len(t) > 3]
        return meaningful[:3]
    except Exception:
        return []


def recommend(movie):
    """
    Hybrid recommender: 70% cosine similarity + 30% IMDB weighted rating.
    Requires movie_list to have a 'weighted_rating' column.
    """
    movie_index = movie_list[movie_list["original_title"] == movie].index[0]
    scores = list(enumerate(similarity[movie_index]))

    max_rating = movie_list["weighted_rating"].max()

    hybrid_scores = []
    for i, cos_score in scores:
        rating_score = movie_list.iloc[i]["weighted_rating"] / max_rating
        final_score = (0.7 * cos_score) + (0.3 * rating_score)
        hybrid_scores.append((i, final_score, cos_score))

    hybrid_scores = sorted(hybrid_scores, reverse=True, key=lambda x: x[1])

    recommended = []
    for i, final_score, cos_score in hybrid_scores[1:6]:
        movie_id = movie_list.iloc[i].movie_id
        details = fetch_movie_details(movie_id)
        reasons = get_match_reasons(movie_index, i)

        recommended.append(
            {
                "title": movie_list.iloc[i].original_title,
                "poster": details["poster"],
                "rating": details["rating"],
                "overview": details["overview"],
                "release_date": details["release_date"],
                "genres": details["genres"],
                "similarity_score": round(cos_score * 100, 1),
                "match_reasons": reasons,
            }
        )
    return recommended


def fuzzy_search(query, all_movies, limit=10):
    """Return movie titles that fuzzy-match the search query."""
    if not query:
        return []
    results = process.extract(query, all_movies, limit=limit)
    return [r[0] for r in results if r[1] > 75]


def extract_movie_from_query(natural_query):
    """
    Use Gemini to extract the most relevant movie title
    from a natural language query like 'something like Inception but funnier'.
    Returns a movie title string or None if extraction fails.
    """
    if not GEMINI_API_KEY:
        return None
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = f"""You are a movie assistant. A user wants a movie recommendation.
Your job is to return a single Hollywood movie title (from before 2016) that best matches their request.

Query: "{natural_query}"

Rules:
- Reply with ONLY the movie title, nothing else
- No punctuation, no explanation  
- If they mention a specific movie, return that movie
- If they describe a mood, genre or vibe (like "romantic movie" or "something funny"), return the most iconic Hollywood movie that fits
- Only Hollywood movies released before 2016
- Examples: "romantic movie" → Titanic"""

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception:
        return None


# =========================
# SESSION STATE INIT
# =========================
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = movies[0]
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "ai_query" not in st.session_state:
    st.session_state.ai_query = ""


# =========================
# UI — HEADER
# =========================
st.title("🎬 Movie Recommendation System")
st.caption("Discover movies similar to your favourites")
st.markdown("---")

# =========================
# UI — AI NATURAL LANGUAGE SEARCH
# =========================
st.markdown("### 🤖 Ask in natural language")
ai_col, ai_btn_col = st.columns([4, 1])

with ai_col:
    ai_query = st.text_input(
        "Describe what you want to watch",
        placeholder='e.g. "something like Interstellar but funnier" or "a dark thriller like Gone Girl"',
        key="ai_input",
    )

with ai_btn_col:
    st.markdown("<br>", unsafe_allow_html=True)
    ai_search_clicked = st.button("🔍 Ask AI")

if ai_search_clicked and ai_query:
    with st.spinner("Asking AI..."):
        extracted_movie = extract_movie_from_query(ai_query)

    if extracted_movie:
        # fuzzy match extracted title against dataset
        matches = fuzzy_search(extracted_movie, movies)
        if matches:
            st.session_state.selected_movie = matches[0]
            st.markdown(
                f'<div class="ai-banner">🤖 AI understood: <strong>{extracted_movie}</strong> → matched to <strong>{matches[0]}</strong> in dataset</div>',
                unsafe_allow_html=True,
            )
        else:
            st.warning(f"AI found '{extracted_movie}' but it's not in our dataset (Hollywood movies up to 2016 only).")
    else:
        st.warning("AI couldn't understand the query. Try being more specific.")

st.markdown("---")

# =========================
# UI — SEARCH + CONTROLS
# =========================
col_search, col_surprise = st.columns([4, 1])

with col_search:
    search_query = st.text_input(
        "Or search by movie name directly",
        placeholder="Start typing a movie name...",
        value=st.session_state.search_query,
    )

with col_surprise:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🎲 Surprise me"):
        st.session_state.selected_movie = random.choice(movies)
        st.session_state.search_query = ""
        search_query = ""

# Movie selection logic
if search_query:
    matches = fuzzy_search(search_query, movies)
    if matches:
        selected_movie = st.selectbox("Select from results", matches)
    else:
        st.warning(
            "⚠️ No movies found. Our dataset has Hollywood movies up to 2016 only - Bollywood, anime, or recent movies won't appear.")
        st.stop()
else:
    selected_movie = st.selectbox(
        "Or browse all movies",
        movies,
        index=int(list(movies).index(st.session_state.selected_movie))
        if st.session_state.selected_movie in movies
        else 0,
    )

st.session_state.selected_movie = selected_movie

# Show selected movie
st.markdown(
    f'<div class="selected-movie-banner">📽️ Showing recommendations for: <strong>{selected_movie}</strong></div>',
    unsafe_allow_html=True,
)

# =========================
# UI — RECOMMEND BUTTON
# =========================
if st.button("🔍 Recommend Movies"):
    with st.spinner("Fetching recommendations..."):
        recommended_movies = recommend(selected_movie)

    st.subheader("Recommended for you")
    cols = st.columns(5)

    for idx, movie in enumerate(recommended_movies):
        with cols[idx]:
            m_poster = movie["poster"]
            m_title = movie["title"]
            m_rating = movie["rating"]
            m_genres = movie["genres"]
            m_score = movie["similarity_score"]
            m_reasons = movie["match_reasons"]

            if m_reasons:
                reasons_str = " · ".join(r.replace("_", " ").title() for r in m_reasons)
                reasons_html = f'<div class="match-reasons">🔗 Matched: {reasons_str}</div>'
            else:
                reasons_html = f'<div class="match-reasons">🔗 Similarity: {m_score}%</div>'

            card_html = f"""
            <div class="movie-card">
                <img class="movie-poster" src="{m_poster}" alt="{m_title}">
                <div class="movie-content">
                    <div class="movie-title">{m_title}</div>
                    <div class="movie-rating">⭐ {m_rating}/10</div>
                    <div class="movie-genre">🎭 {m_genres}</div>
                    {reasons_html}
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

            with st.expander("📖 Overview"):
                st.caption(movie["overview"])
                st.caption(f"📅 Release: {movie['release_date']}")

# =========================
# UI — FOOTER
# =========================
st.markdown("---")