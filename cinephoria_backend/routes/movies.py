# routes/movies.py
from flask import Blueprint, jsonify, request
import requests
from cinephoria_backend.config import TMDB_API_URL, HEADERS


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
    

@movies_bp.route('/movie/<int:movie_id>/release_dates', methods=['GET'])
def get_movie_release_dates(movie_id):
    # URL für die TMDB-API mit der spezifischen Film-ID
    url = f"{TMDB_API_URL}/{movie_id}/release_dates"
    
    # Anfrage an die API senden
    response = requests.get(url, headers=HEADERS)
    
    # Erfolgreiche Antwort zurückgeben
    if response.status_code == 200:
        # JSON-Antwort parsen
        data = response.json()
        
        # Filtere nur den Eintrag mit 'iso_3166_1': 'DE'
        german_release = next((item for item in data['results'] if item['iso_3166_1'] == 'DE'), None)
        
        if german_release:
            return jsonify(german_release)
        else:
            return jsonify({"error": "No release date found for Germany (DE)"}), 404
    else:
        # Fehler behandeln und Fehlermeldung zurückgeben
        return jsonify({"error": f"Unable to fetch details for movie ID {movie_id}"}), response.status_code
    

@movies_bp.route('/movie/<int:movie_id>/trailer_url', methods=['GET'])
def get_movie_trailer_url(movie_id):
    # URL für die TMDB-API mit der spezifischen Film-ID
    url = f"{TMDB_API_URL}/{movie_id}/videos?language=de-DE"

    # Anfrage an die API senden
    response = requests.get(url, headers=HEADERS)
    
    # Erfolgreiche Antwort zurückgeben
    if response.status_code == 200:
        data = response.json()
        
        # Filtert den Eintrag mit 'type' == 'Trailer' und 'site' == 'YouTube'
        trailer = next((item for item in data.get('results', []) if item.get('type') == 'Trailer' and item.get('site') == 'YouTube'), None)
        
        if trailer and 'key' in trailer:
            embed_url = f"https://www.youtube.com/embed/{trailer['key']}"
            return jsonify({"trailer_url": embed_url}), 200
        else:
            return jsonify({"error": "No Trailer found."}), 404
    else:
        return jsonify({"error": f"Unable to fetch Trailer for movie ID {movie_id}"}), response.status_code