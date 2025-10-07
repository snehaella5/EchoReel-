import os
import sys
import pickle
import streamlit as st
import requests  # 👈 For API calls

# --- API Key  ---
OMDB_API_KEY = "2e87f422"   # 👈 paste key

# --- Custom UI/UX ---
st.set_page_config(
    page_title="Echoreel : A Content-Based Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

# Dark theme colors
st.markdown("""
<style>
body {
    background-color: #0B0C10;
    color: #C5C6C7;
    font-family: 'Courier New', monospace;
}
h1 {
    color: #66FCF1;
    font-family: 'Courier New', monospace;
    font-size: 38px;
}
.stButton>button {
    background-color: #45A29E;
    color: #0B0C10;
    height: 3em;
    width: 250px;
    font-size: 16px;
    border-radius: 10px;
}
.stSelectbox>div {
    color: #1F2833;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# --- Define pickle file paths directly ---
MOVIE_LIST_PATH = "movies_recommender_artifacts/serialized_objects/movie_list.pkl"
SIMILARITY_PATH = "movies_recommender_artifacts/trained_model/similarity.pkl"

class Recommendation:
    def __init__(self):
        try:
            self.movies = pickle.load(open(MOVIE_LIST_PATH, 'rb'))
            self.similarity = pickle.load(open(SIMILARITY_PATH, 'rb'))
        except Exception as e:
            st.error(f"Error loading files: {e}")
            sys.exit()

    def fetch_poster(self, movie_title):
        """Fetch poster using OMDb API"""
        try:
            url = f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}"
            response = requests.get(url)
            data = response.json()
            if "Poster" in data and data["Poster"] != "N/A":
                return data["Poster"]
            else:
                return "https://via.placeholder.com/150"  # fallback poster
        except:
            return "https://via.placeholder.com/150"

    def recommend(self, movie):
        try:
            index = self.movies[self.movies['title'] == movie].index[0]
            distances = sorted(list(enumerate(self.similarity[index])), reverse=True, key=lambda x: x[1])
            recommended_movie_names = []
            recommended_movie_posters = []
            for i in distances[1:6]:
                movie_title = self.movies.iloc[i[0]].title
                recommended_movie_posters.append(self.fetch_poster(movie_title))
                recommended_movie_names.append(movie_title)
            return recommended_movie_names, recommended_movie_posters
        except Exception as e:
            st.error(f"Error in recommendation: {e}")
            return [], []

    def recommendations_engine(self, selected_movie):
        recommended_movie_names, recommended_movie_posters = self.recommend(selected_movie)
        if recommended_movie_names:
            cols = st.columns(5)
            for idx, col in enumerate(cols):
                col.text(recommended_movie_names[idx])
                col.image(recommended_movie_posters[idx])


# --- Main App ---
st.markdown("<h1>EchoReel : A Content-Based Movie Recommendation System</h1>", unsafe_allow_html=True)
st.text("ML-Driven Recommendations for the Curious Viewer 🎥")

# Initialize recommendation engine
obj = Recommendation()
movie_list = obj.movies['title'].values
selected_movie = st.selectbox("Select a movie", movie_list)

# Show recommendations button
if st.button("Show Recommendation"):
    obj.recommendations_engine(selected_movie)
