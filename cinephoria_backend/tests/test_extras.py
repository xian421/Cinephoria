import os
os.environ["SECRET_KEY"] = "testsecret"  # Muss vor allen Importen gesetzt werden!

import json
from datetime import datetime, timedelta, timezone
from unittest import mock

import pytest
import psycopg2.extras
import requests
import jwt

from cinephoria_backend.app import app
from cinephoria_backend.config import SECRET_KEY, TMDB_API_URL, HEADERS

# Erzeuge gültige Tokens
user_payload = {
    "user_id": 10,
    "role": "user",
    "exp": datetime.now(timezone.utc) + timedelta(hours=1)
}
user_token = jwt.encode(user_payload, SECRET_KEY, algorithm="HS256")

admin_payload = {
    "user_id": 1,
    "role": "admin",
    "exp": datetime.now(timezone.utc) + timedelta(hours=1)
}
admin_token = jwt.encode(admin_payload, SECRET_KEY, algorithm="HS256")

# Hilfsfunktion: Erzeugt einen Fake-Datenbankkontextmanager mit gegebenem Cursor
def fake_db_conn(cursor):
    conn = mock.MagicMock()
    conn.__enter__.return_value = conn
    conn.cursor.return_value.__enter__.return_value = cursor
    return conn

# 1. Test: GET /bookings
def test_get_user_bookings_success():
    # Simuliere DB-Ergebnis: eine Buchung mit allen nötigen Feldern
    fake_booking = {
        "booking_id": 100,
        "showtime_id": 200,
        "total_amount": 50.0,
        "payment_status": "completed",
        "paypal_order_id": "order_123",
        "created_at": datetime(2025, 2, 1, 12, 0, 0),
        "movie_id": 555,
        "screen_id": 3,
        "start_time": datetime(2025, 2, 1, 14, 0, 0),
        "end_time": datetime(2025, 2, 1, 16, 0, 0),
        "screen_name": "Hauptscreen",
        # Simuliere bereits aggregierte Sitzplätze als JSON-ähnliche Liste
        "seats": [{"seat_id": 1, "price": "10", "row": "A", "number": 1, "seat_type": "normal", "seat_type_discount_id": None}]
    }
    cursor = mock.MagicMock()
    cursor.fetchall.return_value = [fake_booking]
    conn = fake_db_conn(cursor)

    # Patch die DB-Funktion
    with mock.patch("cinephoria_backend.routes.extras.get_db_connection", return_value=conn):
        # Patch den externen Request an TMDB: Wir simulieren eine Antwort für movie_id 555
        fake_tmdb_response = mock.MagicMock()
        fake_tmdb_response.status_code = 200
        fake_tmdb_response.json.return_value = {
            "title": "Test Movie",
            "poster_path": "/test.jpg"
        }
        with mock.patch("cinephoria_backend.routes.extras.requests.get", return_value=fake_tmdb_response):
            client = app.test_client()
            response = client.get(
                "/bookings",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            data = response.get_json()
            assert response.status_code == 200
            assert "bookings" in data
            # Prüfe, ob die Buchung richtig formatiert ist
            booking = data["bookings"][0]
            assert booking["booking_id"] == 100
            assert booking["movie_title"] == "Test Movie"
            # created_at, start_time, end_time sollten ISO-Strings sein
            assert isinstance(booking["created_at"], str)
            assert isinstance(booking["start_time"], str)

# 2. Test: GET /user/points
def test_get_user_points_success():
    cursor = mock.MagicMock()
    # Simuliere, dass der Benutzer 120 Punkte hat
    cursor.fetchone.return_value = [120]
    conn = fake_db_conn(cursor)

    with mock.patch("cinephoria_backend.routes.extras.get_db_connection", return_value=conn):
        client = app.test_client()
        response = client.get(
            "/user/points",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        data = response.get_json()
        assert response.status_code == 200
        assert data.get("points") == 120

# 3. Test: POST /user/points/redeem
def test_redeem_points_success():
    cursor = mock.MagicMock()
    # Simuliere: Zuerst: Belohnung existiert und erfordert exakt 50 Punkte
    # Zweitens: user_points zeigt 100 Punkte an
    cursor.fetchone.side_effect = [
        (50,),  # SELECT points FROM rewards WHERE reward_id = %s
        (100,)  # SELECT points FROM user_points WHERE user_id = %s FOR UPDATE
    ]
    conn = fake_db_conn(cursor)

    with mock.patch("cinephoria_backend.routes.extras.get_db_connection", return_value=conn):
        client = app.test_client()
        payload = {"points": 50, "reward_id": 10}
        response = client.post(
            "/user/points/redeem",
            json=payload,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        data = response.get_json()
        assert response.status_code == 200
        assert "erfolgreich" in data.get("message", "")

# 4. Test: GET /user/points/transactions
def test_get_points_transactions_success():
    # Simuliere DB-Ergebnis: Eine Transaktion
    fake_transaction = {
        "transaction_id": 900,
        "points_change": -50,
        "description": "Einlösung von Punkten für Belohnung",
        "timestamp": datetime(2025, 2, 1, 15, 0, 0),
        "reward_id": 10,
        "reward_title": "Test Reward",
        "reward_points": 50,
        "reward_image": "image.jpg",
        "reward_description": "Beschreibung Reward"
    }
    cursor = mock.MagicMock()
    cursor.fetchall.return_value = [fake_transaction]
    conn = fake_db_conn(cursor)

    with mock.patch("cinephoria_backend.routes.extras.get_db_connection", return_value=conn):
        client = app.test_client()
        response = client.get(
            "/user/points/transactions",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        data = response.get_json()
        assert response.status_code == 200
        assert "transactions" in data
        transaction = data["transactions"][0]
        assert transaction["transaction_id"] == 900
        assert transaction["reward"]["title"] == "Test Reward"

# 5. Test: GET /rewards
def test_get_rewards_success():
    fake_rewards = [
        {"reward_id": 10, "title": "Reward A", "points": 50, "description": "Desc", "image": "img.jpg"},
        {"reward_id": 11, "title": "Reward B", "points": 100, "description": "Desc B", "image": "img2.jpg"}
    ]
    cursor = mock.MagicMock()
    cursor.fetchall.return_value = fake_rewards
    conn = fake_db_conn(cursor)

    with mock.patch("cinephoria_backend.routes.extras.get_db_connection", return_value=conn):
        client = app.test_client()
        response = client.get("/rewards")
        data = response.get_json()
        assert response.status_code == 200
        assert "rewards" in data
        assert len(data["rewards"]) == 2

# 6. Test: POST /rewards (Admin)
def test_add_reward_success():
    cursor = mock.MagicMock()
    # Simuliere einen erfolgreichen Insert (keine Rückgabe von rowcount, Commit erfolgt)
    conn = fake_db_conn(cursor)

    with mock.patch("cinephoria_backend.routes.extras.get_db_connection", return_value=conn):
        client = app.test_client()
        payload = {"title": "Neues Reward", "points": 75, "description": "Test", "image": "img.png"}
        response = client.post(
            "/rewards",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()
        # Im Erfolgsfall wird ein 201 zurückgegeben
        assert response.status_code == 201
        assert "hinzugefügt" in data.get("message", "")

# 7. Test: PUT /rewards/<int:reward_id> (Admin)
def test_update_reward_success():
    cursor = mock.MagicMock()
    # Simuliere, dass rowcount > 0 (Update erfolgte)
    cursor.rowcount = 1
    conn = fake_db_conn(cursor)

    with mock.patch("cinephoria_backend.routes.extras.get_db_connection", return_value=conn):
        client = app.test_client()
        payload = {"title": "Updated Reward", "points": 80, "description": "Update", "image": "img_updated.png"}
        response = client.put(
            "/rewards/10",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()
        assert response.status_code == 200
        assert "aktualisiert" in data.get("message", "")

# 8. Test: DELETE /rewards/<int:reward_id> (Admin)
def test_delete_reward_success():
    cursor = mock.MagicMock()
    # Simuliere, dass ein Reward gelöscht wird (rowcount > 0)
    cursor.rowcount = 1
    conn = fake_db_conn(cursor)

    with mock.patch("cinephoria_backend.routes.extras.get_db_connection", return_value=conn):
        client = app.test_client()
        response = client.delete(
            "/rewards/10",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()
        assert response.status_code == 200
        assert "gelöscht" in data.get("message", "")

# 9. Test: GET /leaderboard
def test_get_leaderboard_success():
    # Simuliere DB-Ergebnis: Zwei User
    fake_users = [
        {
            "user_id": 1,
            "nickname": "Alice",
            "points": 150,
            "profile_image": "alice.jpg",
            "bookings": 3,
            "last_booking": datetime(2025, 2, 1, 18, 0, 0),
            "total_duration": 120.0
        },
        {
            "user_id": 2,
            "nickname": "Bob",
            "points": 100,
            "profile_image": "bob.jpg",
            "bookings": 2,
            "last_booking": datetime(2025, 2, 1, 17, 0, 0),
            "total_duration": 90.0
        }
    ]
    cursor = mock.MagicMock()
    cursor.fetchall.return_value = fake_users
    conn = fake_db_conn(cursor)

    with mock.patch("cinephoria_backend.routes.extras.get_db_connection", return_value=conn):
        client = app.test_client()
        response = client.get("/leaderboard")
        data = response.get_json()
        assert response.status_code == 200
        assert "leaderboard" in data
        assert len(data["leaderboard"]) == 2
        # Prüfe, ob die User-Daten enthalten sind
        assert data["leaderboard"][0]["nickname"] in ["Alice", "Bob"]
