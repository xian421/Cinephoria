import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL')
    TMDB_BEARER_TOKEN = os.getenv('TMDB_BEARER_TOKEN')
    PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')
    # Füge weitere Konfigurationen hinzu, die du benötigst
