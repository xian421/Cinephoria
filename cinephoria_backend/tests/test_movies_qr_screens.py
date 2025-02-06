import os
os.environ["SECRET_KEY"] = "testsecret"  # Muss vor allen Importen gesetzt werden!

import json
from datetime import datetime, timedelta, timezone
from unittest import mock

import pytest
import requests

from flask import jsonify
from cinephoria_backend.app import app
from cinephoria_backend.config import TMDB_API_URL, HEADERS

#############################################
# Tests für movies.py
#############################################

# Test für /movies/now_playing
def test_get_now_playing_success():
    # Simuliere für jede Seite eine Antwort mit "results"
    fake_movie = {"id": 123, "title": "Test Movie", "poster_path": "/test.jpg"}
    fake_response = {"results": [fake_movie]}
    
    # Erstelle einen Fake-Response-Mock, der status_code 200 liefert
    fake_get = mock.MagicMock()
    fake_get.return_value.status_code = 200
    fake_get.return_value.json.return_value = fake_response

    with mock.patch("cinephoria_backend.routes.movies.requests.get", fake_get):
        client = app.test_client()
        response = client.get("/movies/now_playing")
        data = response.get_json()
        assert response.status_code == 200
        # Da 5 Seiten abgefragt werden, erwarten wir 5-faches des Fake-Movies
        assert "results" in data
        assert len(data["results"]) == 5
        for movie in data["results"]:
            assert movie.get("poster_path")  # Nur Filme mit poster_path kommen rein

# Test für /movies/upcoming
def test_get_upcoming_success():
    fake_upcoming = {"results": [{"id": 321, "title": "Upcoming Movie"}]}
    fake_get = mock.MagicMock()
    fake_get.return_value.status_code = 200
    fake_get.return_value.json.return_value = fake_upcoming

    with mock.patch("cinephoria_backend.routes.movies.requests.get", fake_get):
        client = app.test_client()
        response = client.get("/movies/upcoming")
        data = response.get_json()
        assert response.status_code == 200
        assert data == fake_upcoming

# Test für /movies/<int:movie_id>
def test_get_movie_details_success():
    movie_id = 555
    fake_details = {"id": movie_id, "title": "Detail Movie"}
    fake_get = mock.MagicMock()
    fake_get.return_value.status_code = 200
    fake_get.return_value.json.return_value = fake_details

    with mock.patch("cinephoria_backend.routes.movies.requests.get", fake_get):
        client = app.test_client()
        response = client.get(f"/movies/{movie_id}")
        data = response.get_json()
        assert response.status_code == 200
        assert data == fake_details

# Test für /movie/<int:movie_id>/release_dates
def test_get_movie_release_dates_success():
    movie_id = 777
    # Simuliere eine TMDB-Antwort, in der unter "results" ein Eintrag mit iso_3166_1 "DE" existiert
    fake_release = {
        "results": [
            {"iso_3166_1": "US", "release_dates": []},
            {"iso_3166_1": "DE", "release_dates": [{"release_date": "2025-02-06T00:00:00.000Z"}]}
        ]
    }
    fake_get = mock.MagicMock()
    fake_get.return_value.status_code = 200
    fake_get.return_value.json.return_value = fake_release

    with mock.patch("cinephoria_backend.routes.movies.requests.get", fake_get):
        client = app.test_client()
        response = client.get(f"/movie/{movie_id}/release_dates")
        data = response.get_json()
        assert response.status_code == 200
        # Wir erwarten, dass der DE-Eintrag zurückgegeben wird
        assert data.get("iso_3166_1") == "DE"

# Test für /movie/<int:movie_id>/trailer_url
def test_get_movie_trailer_url_success():
    movie_id = 888
    fake_video = {
        "results": [
            {"type": "Teaser", "site": "YouTube", "key": "abc123"},
            {"type": "Trailer", "site": "YouTube", "key": "trailerKey"}
        ]
    }
    fake_get = mock.MagicMock()
    fake_get.return_value.status_code = 200
    fake_get.return_value.json.return_value = fake_video

    with mock.patch("cinephoria_backend.routes.movies.requests.get", fake_get):
        client = app.test_client()
        response = client.get(f"/movie/{movie_id}/trailer_url")
        data = response.get_json()
        assert response.status_code == 200
        # Wir erwarten eine eingebettete YouTube-URL mit dem Trailer-Key
        assert "trailer_url" in data
        assert "trailerKey" in data["trailer_url"]

#############################################
# Tests für QR-Code Endpunkte
#############################################

def fake_db_cursor_with_booking(booking, seats):
    cursor = mock.MagicMock()
    # Erste Abfrage liefert den Buchungseintrag
    cursor.fetchone.side_effect = [booking]
    # Danach liefert fetchall() die Sitzplätze
    cursor.fetchall.return_value = seats
    return cursor

# Test für /read/qrcode/<token>
def test_read_qrcode_success():
    # Da die Route 'WHERE qr_seite = %s' verwendet,
    # muss unser Fake-Booking in der Spalte 'qr_seite' dasselbe haben wie 'token'.
    token = "qrcodeToken123"
    
    fake_booking = {
        "booking_id": 1000,
        "user_id": 50,
        "booking_time": datetime(2025, 2, 1, 12, 0, 0),
        "payment_status": "completed",
        "total_amount": 25.0,
        "created_at": datetime(2025, 2, 1, 12, 5, 0),
        "paypal_order_id": "orderXYZ",
        "email": "test@example.com",
        "nachname": "Mustermann",
        "vorname": "Max",
        # Hier haben wir BEIDES gesetzt, damit der Code auch 'qr_token' zurückliefern kann.
        "qr_token": "abcDEF",
        "qr_seite": token
    }

    fake_seats = [
        {
            "nummer": 10,
            "reihe": "B",
            "type": "normal",
            "farbe": "blue",
            "type_icon": "icon.png",
            "discount_percentage": None,
            "discount_amount": None,
            "discount": "Student",
            "discount_infos": "10% Rabatt",
            "movie_id": 555,
            "start_time": datetime(2025, 2, 1, 14, 0, 0),
            "end_time": datetime(2025, 2, 1, 16, 0, 0),
            "kinosaal": "Saal 1"
        }
    ]
    fake_cursor = fake_db_cursor_with_booking(fake_booking, fake_seats)
    fake_conn = mock.MagicMock()
    fake_conn.__enter__.return_value = fake_conn
    fake_conn.cursor.return_value.__enter__.return_value = fake_cursor

    # Hier patchen wir 'cinephoria_backend.routes.qr.get_db_connection',
    # weil in 'qr.py' das get_db_connection wirklich aufgerufen wird.
    with mock.patch("cinephoria_backend.routes.qr.get_db_connection", return_value=fake_conn):
        client = app.test_client()
        response = client.get(f"/read/qrcode/{token}")
        data = response.get_json()
        
        assert response.status_code == 200
        assert data.get("booking_id") == 1000
        assert "movies" in data
        # Da wir einen Film in seats simuliert haben, sollte die Liste nicht leer sein
        assert len(data["movies"]) == 1

# Test für /mitarbeiter/read/qrcode/<token>
def test_read_qrcode_mitarbeiter_success():
    # Da hier 'WHERE qr_token = %s' verwendet wird,
    # setzen wir in unserem Fake-Booking ebenfalls denselben Wert in 'qr_token'.
    token = "qrcodeMitarbeiterToken456"
    
    fake_booking = {
        "booking_id": 2000,
        "user_id": 60,
        "booking_time": datetime(2025, 3, 1, 12, 0, 0),
        "payment_status": "completed",
        "total_amount": 30.0,
        "created_at": datetime(2025, 3, 1, 12, 5, 0),
        "paypal_order_id": "orderABC",
        "email": "mitarbeiter@example.com",
        "nachname": "Muster",
        "vorname": "Erika",
        "qr_token": token  # Muss zum Routenaufruf passen
    }

    fake_seats = [
        {
            "nummer": 5,
            "reihe": "A",
            "type": "VIP",
            "farbe": "red",
            "type_icon": "vip.png",
            "discount_percentage": 20,
            "discount_amount": 5,
            "discount": "VIP Rabatt",
            "discount_infos": "20% Rabatt",
            "movie_id": 666,
            "start_time": datetime(2025, 3, 1, 18, 0, 0),
            "end_time": datetime(2025, 3, 1, 20, 0, 0),
            "kinosaal": "Saal 2"
        }
    ]
    fake_cursor = fake_db_cursor_with_booking(fake_booking, fake_seats)
    fake_conn = mock.MagicMock()
    fake_conn.__enter__.return_value = fake_conn
    fake_conn.cursor.return_value.__enter__.return_value = fake_cursor

    with mock.patch("cinephoria_backend.routes.qr.get_db_connection", return_value=fake_conn):
        client = app.test_client()
        response = client.get(f"/mitarbeiter/read/qrcode/{token}")
        data = response.get_json()
        
   

#############################################
# Tests für screens.py
#############################################
def test_get_cinemas_success():
    fake_rows = [
        (1, "Cinema One", "Ort A", "0123456789"),
        (2, "Cinema Two", "Ort B", "0987654321")
    ]
    fake_cursor = mock.MagicMock()
    fake_cursor.fetchall.return_value = fake_rows
    fake_conn = mock.MagicMock()
    fake_conn.__enter__.return_value = fake_conn
    fake_conn.cursor.return_value.__enter__.return_value = fake_cursor

    with mock.patch("cinephoria_backend.routes.screens.get_db_connection", return_value=fake_conn):
        client = app.test_client()
        response = client.get("/cinemas")
        data = response.get_json()
        assert response.status_code == 200
        assert "cinemas" in data
        assert len(data["cinemas"]) == 2
        assert data["cinemas"][0]["name"] == "Cinema One"

def test_get_screens_success():
    fake_rows = [
        (10, "Saal 1", 100, "Standard", datetime(2025, 1, 1), datetime(2025, 1, 1)),
        (11, "Saal 2", 80, "IMAX", datetime(2025, 1, 2), datetime(2025, 1, 2))
    ]
    fake_cursor = mock.MagicMock()
    fake_cursor.fetchall.return_value = fake_rows
    fake_conn = mock.MagicMock()
    fake_conn.__enter__.return_value = fake_conn
    fake_conn.cursor.return_value.__enter__.return_value = fake_cursor

    with mock.patch("cinephoria_backend.routes.screens.get_db_connection", return_value=fake_conn):
        client = app.test_client()
        response = client.get("/screens?cinema_id=1")
        data = response.get_json()
        assert response.status_code == 200
        assert "screens" in data
        assert len(data["screens"]) == 2
        assert data["screens"][0]["name"] == "Saal 1"
