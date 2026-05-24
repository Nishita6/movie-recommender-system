<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white" alt="Jupyter Notebook" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  
  <h1 align="center">🎬 Movie Recommender System</h1>
  <p align="center">A Content-Based Movie Recommender System built using Python, Jupyter Notebook, and Streamlit.</p>
</div>

<hr />

## 📌 Overview
This repository contains a **Content-Based Movie Recommender System**. The system recommends movies similar to a user's selection based on various metadata features (such as genres, keywords, cast, and crew). It uses **Cosine Similarity** to calculate the distance between movie vectors and suggest the top matches.

The project is deployed as an interactive web application using **Streamlit**.

<hr />

## 🔗 Live Application:
https://movie-recommender-system6.streamlit.app/

## 📁 Repository Structure
The project consists of the following key files:

* **`movie-recommender.ipynb`**: The Jupyter Notebook where the data preprocessing, exploratory data analysis (EDA), and machine learning model architecture are developed.
* **`app.py`**: The Streamlit application script that serves the user interface and handles frontend interactions.
* **`movie_list.pkl`**: A pickled DataFrame containing processed movie details used by the app.
* **`similarity.pkl`**: A pickled matrix representing the calculated cosine similarity scores between all movies.

<hr />

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Nishita6/movie-recommender-system.git
cd movie-recommender-system
```
### 2. Install Dependencies
```bash
pip install streamlit pandas scikit-learn requests
```
### 3. Run the Application
```bash
streamlit run app.py
```
