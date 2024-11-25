import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Dein TMDb API-Key
TMDB_API_KEY = "11f3a5009a106254982604a825c553d1"

# Route, um aktuelle Filme von TMDb zu holen
@app.route('/movies', methods=['GET'])
def get_movies():
    url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=en-US&page=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Nur relevante Informationen extrahieren
        movies = [
            {"id": movie["id"], "title": movie["title"], "release_date": movie["release_date"]}
            for movie in data.get("results", [])
        ]
        return jsonify(movies)
    else:
        return jsonify({"error": "Unable to fetch movies"}), response.status_code

if __name__ == '__main__': 
    app.run(debug=True)
