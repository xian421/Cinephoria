import os

# SECRET_KEY setzen, bevor config.py importiert wird
os.environ["SECRET_KEY"] = "testsecret"

# Jetzt erst config importieren!
from cinephoria_backend.config import SECRET_KEY, DATABASE_URL, PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET

def test_secret_key():
    assert SECRET_KEY == "testsecret"  # Falls du es in den Umgebungsvariablen gesetzt hast

def test_database_url():
    os.environ["DATABASE_URL"] = "postgres://test:test@localhost:5432/test_db"
    from cinephoria_backend.config import DATABASE_URL
    assert DATABASE_URL == "postgres://test:test@localhost:5432/test_db"
