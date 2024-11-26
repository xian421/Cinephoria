import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import jwt
import datetime

app = Flask(__name__)
CORS(app, origins=["https://cinephoria-theta.vercel.app"])

# Datenbankkonfiguration
DATABASE_URL = "postgres://u9v1p2ouoehmll:pa83fe38fd05666e13bce1b16c58e23ecc849ac08945632f8986c00ce25bd250e@c3gtj1dt5vh48j.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/db5lga5e41bidv"

# Verbindung zur Datenbank herstellen
connection = psycopg2.connect(DATABASE_URL)
connection.autocommit = True  # Automatisches Commit für Änderungen
cursor = connection.cursor()



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
            # Filter: Nur Filme mit einem gültigen `poster_path` hinzufügen
            filtered_results = [
                movie for movie in data['results'] if movie.get('poster_path')
            ]
            results.extend(filtered_results)
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
    




SECRET_KEY = "dein_geheimer_schlüssel"  # Ändere das in eine sichere, lange Zeichenfolge

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'E-Mail und Passwort sind erforderlich'}), 400

    try:
        # Benutzer und Passwort-Hash abrufen
        cursor.execute("SELECT id, password, vorname, nachname FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()

        if not result:
            return jsonify({'error': 'Ungültige E-Mail oder Passwort'}), 401

        user_id, stored_password, vorname, nachname = result

        # Passwort überprüfen
        cursor.execute("SELECT crypt(%s, %s) = %s AS password_match", (password, stored_password, stored_password))
        is_valid = cursor.fetchone()[0]

        if is_valid:
            initials = f"{vorname[0].upper()}{nachname[0].upper()}"
            # JWT-Token generieren
            token = jwt.encode({
                'user_id': user_id,
                'email': email,
                'first_name': vorname,  
                'last_name': nachname, 
                'initials': initials, 
                'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
            }, SECRET_KEY, algorithm='HS256')

            return jsonify({
                'message': 'Login erfolgreich',
                'token': token,
                'first_name': vorname,
                'last_name': nachname,
                'initials': initials
            }), 200
        else:
            return jsonify({'error': 'Ungültige E-Mail oder Passwort'}), 401

    except Exception as e:
        print(f"Fehler: {e}")
        return jsonify({'error': 'Fehler bei der Anmeldung'}), 500



@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    vorname = data.get('first_name')  # Mapping von "first_name" auf "vorname"
    nachname = data.get('last_name')  # Mapping von "last_name" auf "nachname"
    email = data.get('email')
    password = data.get('password')

    if not vorname or not nachname or not email or not password:
        return jsonify({'error': 'Alle Felder sind erforderlich'}), 400

    try:
        # Prüfen, ob der Benutzer schon existiert
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({'error': 'Benutzer mit dieser E-Mail existiert bereits'}), 409

        # Passwort hashen mit der PostgreSQL-Methode
        cursor.execute(
            "INSERT INTO users (vorname, nachname, email, password) VALUES (%s, %s, %s, crypt(%s, gen_salt('bf')))",
            (vorname, nachname, email, password),
        )
        return jsonify({'message': 'Registrierung erfolgreich'}), 201

    except Exception as e:
        print(f"Fehler bei der Registrierung: {e}")  # Fehlerausgabe für Debugging
        return jsonify({'error': 'Ein Fehler ist aufgetreten'}), 500




if __name__ == '__main__':
    app.run(debug=True)
