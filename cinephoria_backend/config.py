# cinephoria_backend/config.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Lade Umgebungsvariablen
DATABASE_URL = os.getenv("DATABASE_URL")
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
TMDB_BEARER_TOKEN = os.getenv("TMDB_BEARER_TOKEN")
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")



# Konfiguration für PayPal und TMDb
PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"
TMDB_API_URL = "https://api.themoviedb.org/3/movie"
HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_BEARER_TOKEN}"
}

# Funktion, um eine Datenbankverbindung zu erstellen
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)
