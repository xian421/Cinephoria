import os
os.environ["SECRET_KEY"] = "testsecret"

from cinephoria_backend.routes import paypal
from cinephoria_backend.config import PAYPAL_API_BASE, PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, get_db_connection, SECRET_KEY, TMDB_API_URL, HEADERS, DATABASE_URL, TMDB_BEARER_TOKEN

def test_sum():
    assert 1 + 2 == 3

def test_upper():
    assert "hello".upper() == "HELLO"
