# import requests
# from flask import Flask, jsonify
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)

# # Dein TMDb API-Key
# TMDB_API_KEY = "11f3a5009a106254982604a825c553d1"

# # Route, um aktuelle Filme von TMDb zu holen
# @app.route('/movies', methods=['GET'])
# def get_movies():
#     url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=en-US&page=1"
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#         # Nur relevante Informationen extrahieren
#         movies = [
#             {"id": movie["id"], "title": movie["title"], "release_date": movie["release_date"]}
#             for movie in data.get("results", [])
#         ]
#         return jsonify(movies)
#     else:
#         return jsonify({"error": "Unable to fetch movies"}), response.status_code

# if __name__ == '__main__': 
#     app.run(debug=True)


import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# TMDb API-Konfiguration
TMDB_API_URL = "https://api.themoviedb.org/3/movie"
TMDB_BEARER_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIxMWYzYTUwMDlhMTA2MjU0OTgyNjA0YTgyNWM1NTNkMSIsIm5iZiI6MTczMjU2NTAzNC4wNTkyOTksInN1YiI6IjY3NDRkNzNmNDYyNjBlMTRmYmViNTBjYyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.rT1YsoHHShp4hErZ_LVASnwWLhfXCZ0TLiVw-ScGKUs"

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_BEARER_TOKEN}"
}

@app.route('/movies/now_playing', methods=['GET'])
def get_now_playing():
    results = []
    for i in range(1, 6):  # Seiten von 1 bis 5 durchlaufen
        url = f"{TMDB_API_URL}/now_playing?language=de-DE&page={i}&region=DE"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            results.extend(data['results'])  # Ergebnisse hinzufügen
        else:
            print(f"Fehler bei Seite {i}: {response.status_code}")
    
    # Alle Ergebnisse in ein JSON-Objekt packen
    return jsonify({"results": results})



@app.route('/movies/upcoming', methods=['GET'])
def get_upcoming():
    url = f"{TMDB_API_URL}/upcoming?language=de-DE&page=1&region=DE"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Unable to fetch upcoming movies"}), response.status_code
    
@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    # URL für die TMDB-API mit der spezifischen Film-ID
    url = f"{TMDB_API_URL}/{movie_id}?language=de-DE"
    
    # Anfrage an die API senden
    response = requests.get(url, headers=HEADERS)
    
    # Erfolgreiche Antwort zurückgeben
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        # Fehler behandeln und Fehlermeldung zurückgeben
        return jsonify({"error": f"Unable to fetch details for movie ID {movie_id}"}), response.status_code


if __name__ == '__main__':
    app.run(debug=True)
