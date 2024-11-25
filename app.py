from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)

# CORS aktivieren
CORS(app)

# Beispiel-Routen
@app.route('/')
def home():
    return "Willkommen bei Cinephoria!"

@app.route('/movies')
def movies():
    # Beispiel-Daten (diese würden später aus einer Datenbank kommen)
    return jsonify([
        {"id": 1, "title": "Inception"},
        {"id": 2, "title": "Interstellar"},
        {"id": 3, "title": "The Dark Knight"}
    ])

if __name__ == '__main__':
    app.run(debug=True)
