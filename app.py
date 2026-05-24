import pickle
import pandas as pd
import requests
import streamlit as st

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# =========================
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
    border-radius: 15px 15px 0px 0px;
}
.movie-content {
    padding: 12px;
}
.movie-title {
    font-size: 18px;
    font-weight: bold;
    color: white;
    margin-bottom: 8px;
}
.movie-rating {
    font-size: 16px;
    color: #ff4b6e;
    margin-bottom: 8px;
}
.movie-genre {
    font-size: 13px;
    color: #cfcfcf;
}
.stButton>button {
    width: 100%;
    border-radius: 10px;
    background-color: #E50914;
    color: white;
    font-size: 18px;
    height: 3em;
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================
# HELPER FUNCTIONSxx`
# =========================
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=650ce3590916e66db656a0cf587d5295&language=en-US"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        poster_path = data.get("poster_path")
        if poster_path:
            poster = f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            poster = "https://via.placeholder.com/500x750?text=No+Poster"

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


def recommend(movie):
    movie_index = movie_list[movie_list["original_title"] == movie].index[0]
    movies_list = sorted(
        list(enumerate(similarity[movie_index])),
        reverse=True,
        key=lambda x: x[1],
    )

    recommended_movies = []
    for i in movies_list[1:6]:
        movie_id = movie_list.iloc[i[0]].movie_id
        details = fetch_movie_details(movie_id)
        recommended_movies.append(
            {
                "title": movie_list.iloc[i[0]].original_title,
                "poster": details["poster"],
                "rating": details["rating"],
                "overview": details["overview"],
                "release_date": details["release_date"],
                "genres": details["genres"],
            }
        )
    return recommended_movies


# =========================
# DATA INITIALIZATION
# =========================
movie_list = pickle.load(open("movie_list.pkl", "rb"))
movies = movie_list["original_title"].values
similarity = pickle.load(open("similarity.pkl", "rb"))

# =========================
# UI LAYOUT
# =========================
st.title("Movie Recommendation System")
st.caption("Discover movies similar to your favorites")

selected_movie = st.selectbox("Select a movie", movies)

if st.button("Recommend Movies"):
    with st.spinner("Fetching recommendations..."):
        recommended_movies = recommend(selected_movie)

    st.subheader("Recommended Movies")
    cols = st.columns(5)

    for idx, movie in enumerate(recommended_movies):
        with cols[idx]:
            # Created clean string variables to prevent HTML quote breaking bugs
            m_poster = movie["poster"]
            m_title = movie["title"]
            m_rating = movie["rating"]
            m_genres = movie["genres"]

            card_html = f"""
            <div class="movie-card">
                <img class="movie-poster" src="{m_poster}">
                <div class="movie-content">
                    <div class="movie-title">{m_title}</div>
                    <div class="movie-rating">⭐ {m_rating}/10</div>
                    <div class="movie-genre">🎭 {m_genres}</div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
