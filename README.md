<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white" alt="Jupyter Notebook" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="scikit-learn" />
  <img src="https://img.shields.io/badge/Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white" alt="Gemini" />

  <h1 align="center">🎬 Movie Recommender System</h1>
  <p align="center">A content-based movie recommender with hybrid ranking, explainability, fuzzy search, and natural-language querying - built with Python, scikit-learn, and Streamlit.</p>
</div>
<hr />

## 📌 Overview

This repository contains a **content-based movie recommender system**. It recommends movies similar to a user's selection based on metadata features (genres, keywords, cast, crew), using **cosine similarity** between TF-IDF movie vectors.

On top of the base model, the system adds:
- **Hybrid re-ranking** - blends similarity with an IMDB-style weighted rating so well-matched, well-reviewed movies surface first
- **Explainability** - shows *why* a movie was recommended (shared tags), not just a similarity score
- **Live TMDB data** - posters, ratings, and overviews fetched in real time, not frozen at build time
- **Fuzzy search** - type a partial/misspelled title instead of scrolling a 5000-item dropdown, with a confidence threshold tuned to reject bad matches
- **Natural-language search** - describe what you want ("a dark thriller like Gone Girl", "something funny") and an LLM (Gemini) maps it to a movie in the dataset
- **Surprise Me** - random pick for when you don't know what to search

The project is deployed as an interactive web app using **Streamlit**.

<hr />

## 🔗 Live Application

https://movie-recommender-system6.streamlit.app/

<hr />

## How It Works

```
Raw TMDB metadata (5000 movies)
        │
        ▼
Feature extraction (genres + keywords + cast + crew → combined "tags")
        │
        ▼
TF-IDF / Bag-of-Words vectorization
        │
        ▼
Cosine similarity matrix (movie × movie)
        │
        ▼
Hybrid re-ranking (70% similarity + 30% IMDB-weighted rating)
        │
        ▼
Top 5 recommendations + live TMDB poster/rating + match explanation
```

The similarity matrix is precomputed offline in the notebook and pickled; the app re-ranks and enriches results with live data at request time.

<hr />

## 📁 Repository Structure

* **`movie-recommender.ipynb`** - data preprocessing, EDA, feature engineering, and model build (TF-IDF, cosine similarity, weighted rating)
* **`app.py`** - Streamlit app: UI, recommendation logic, fuzzy search, explainability, Gemini-based NL query parsing
* **`movie_list.pkl`** - pickled DataFrame of processed movie details + weighted ratings
* **`similarity.pkl`** - pickled cosine similarity matrix between all movies
* **`requirements.txt`** - pinned dependencies
* **`.streamlit/secrets.toml`** - API keys (gitignored, not committed)

<hr />

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Nishita6/movie-recommender-system.git
cd movie-recommender-system
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Add API Keys

Create `.streamlit/secrets.toml`:
```toml
TMDB_API_KEY = "your_tmdb_key"
GEMINI_API_KEY = "your_gemini_key"
```

### 4. Run the Application
```bash
streamlit run app.py
```

<hr />

## ⚠️ Limitations

- **Dataset coverage** - built on TMDB 5000, predominantly Hollywood movies released before 2016. Bollywood, anime, and recent releases won't appear; the app surfaces this explicitly instead of returning a misleading fuzzy match.
- **Sparse-metadata movies** - a handful of titles have thin tags in the source dataset and produce weaker matches - a data quality issue, not a modeling one.

<hr />

## 🙏 Credits

Built on the [TMDB 5000 Movie Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata). Originally based on a CampusX tutorial, substantially extended with live API integration, hybrid ranking, explainability, fuzzy search, and natural-language search.
