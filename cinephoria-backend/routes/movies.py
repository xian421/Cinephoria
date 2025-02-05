# routes/movies.py
from flask import Blueprint, jsonify, request
import requests
import os

# Hole dir den TMDB API Bearer Token aus den Umgebungsvariablen
TMDB_BEARER_TOKEN = os.getenv('TMDB_BEARER_TOKEN')
TMDB_API_URL = "https://api.themoviedb.org/3/movie"

# Definiere Headers, die du für TMDB-Anfragen benötigst
HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_BEARER_TOKEN}"
}

# Erstelle einen Blueprint für die Movie-Routen
movies_bp = Blueprint('movies', __name__)

@movies_bp.route('/movies/now_playing', methods=['GET'])
def get_now_playing():
    results = []
    for i in range(1, 6):  # Seiten 1 bis 5 durchlaufen
        url = f"{TMDB_API_URL}/now_playing?language=de-DE&page={i}&region=DE"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            filtered_results = [
                movie for movie in data['results'] if movie.get('poster_path')
            ]
            results.extend(filtered_results)
        else:
            print(f"Fehler bei Seite {i}: {response.status_code}")
    
    return jsonify({"results": results})

@movies_bp.route('/movies/upcoming', methods=['GET'])
def get_upcoming():
    url = f"{TMDB_API_URL}/upcoming?language=de-DE&page=1&region=DE"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Unable to fetch upcoming movies"}), response.status_code

@movies_bp.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    url = f"{TMDB_API_URL}/{movie_id}?language=de-DE"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": f"Unable to fetch details for movie ID {movie_id}"}), response.status_code

# Weitere movie-bezogene Routen können hier ergänzt werden...
