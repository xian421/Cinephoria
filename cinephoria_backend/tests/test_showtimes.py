import os
os.environ["SECRET_KEY"] = "testsecret"  # Muss vor allen Importen gesetzt werden!

import json
from datetime import datetime, timedelta, timezone
from unittest import mock

import pytest
import jwt
from cinephoria_backend.app import app
from cinephoria_backend.config import SECRET_KEY

# Erzeuge einen gültigen Admin-Token
admin_payload = {
    "user_id": 1,
    "role": "admin",
    "exp": datetime.now(timezone.utc) + timedelta(hours=1)
}
admin_token = jwt.encode(admin_payload, SECRET_KEY, algorithm="HS256")

# Hilfsfunktion: Fake-DB-Kontextmanager
def fake_db_conn(return_values, fetchall_return=[]):
    conn = mock.MagicMock()
    cursor = mock.MagicMock()
    cursor.fetchone.side_effect = return_values
    cursor.fetchall.return_value = fetchall_return
    conn.__enter__.return_value = conn
    conn.cursor.return_value.__enter__.return_value = cursor
    return conn

# ----------------------------
# Tests für die Showtimes-Routen
# ----------------------------

# Test für POST /showtimes (Showtime erstellen)
def test_create_showtime_success():
    # Simuliere, dass beim INSERT in die showtimes-Tabelle ein neuer showtime_id (z. B. 10) zurückgegeben wird.
    conn = fake_db_conn(return_values=[(10,)])
    with mock.patch("cinephoria_backend.routes.showtimes.get_db_connection", return_value=conn):
        client = app.test_client()
        payload = {
            "screen_id": 5,
            "movie_id": 100,
            "start_time": "2025-05-01T20:00:00",
            "end_time": "2025-05-01T22:00:00"
        }
        response = client.post(
            "/showtimes",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()
        assert response.status_code == 201, f"Statuscode: {response.status_code}"
        assert "showtime_id" in data
        assert data["showtime_id"] == 10

# Test für GET /showtimes (alle Showtimes filtern nach screen_id)
def test_get_showtimes_success():
    # Simuliere DB-Ergebnis: Zwei Showtimes als Tupel:
    # (showtime_id, movie_id, screen_id, start_time, end_time, screen_name)
    fake_rows = [
        (10, 100, 5, datetime(2025, 5, 1, 20, 0, 0), datetime(2025, 5, 1, 22, 0, 0), "Screen A"),
        (11, 101, 5, datetime(2025, 5, 2, 18, 0, 0), None, "Screen A")
    ]
    conn = fake_db_conn(return_values=[], fetchall_return=fake_rows)
    with mock.patch("cinephoria_backend.routes.showtimes.get_db_connection", return_value=conn):
        client = app.test_client()
        response = client.get("/showtimes?screen_id=5")
        data = response.get_json()
        assert response.status_code == 200
        assert "showtimes" in data
        assert isinstance(data["showtimes"], list)
        assert len(data["showtimes"]) == 2
        # Prüfe, ob die start_time im ISO-Format ist (enthält ein "T")
        assert "T" in data["showtimes"][0]["start_time"]

# Test für GET /showtimes/aktuell (Showtimes von heute)
def test_get_showtimes_today_success():
    now = datetime.now(timezone.utc)
    fake_rows = [
        (20, 102, 6, now, now + timedelta(hours=2), "Screen B")
    ]
    conn = fake_db_conn(return_values=[], fetchall_return=fake_rows)
    with mock.patch("cinephoria_backend.routes.showtimes.get_db_connection", return_value=conn):
        client = app.test_client()
        response = client.get("/showtimes/aktuell")
        data = response.get_json()
        assert response.status_code == 200
        assert "showtimes" in data
        assert len(data["showtimes"]) == 1

# Test für PUT /showtimes/<int:showtime_id> (Showtime aktualisieren)
def test_update_showtime_success():
    conn = fake_db_conn(return_values=[None])
    cursor = conn.cursor.return_value.__enter__.return_value
    cursor.rowcount = 1
    with mock.patch("cinephoria_backend.routes.showtimes.get_db_connection", return_value=conn):
        client = app.test_client()
        payload = {
            "screen_id": 7,
            "movie_id": 105,
            "start_time": "2025-06-01T18:00:00",
            "end_time": "2025-06-01T20:00:00"
        }
        response = client.put(
            "/showtimes/20",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()
        assert response.status_code == 200, f"Statuscode: {response.status_code}"
        assert "Showtime aktualisiert" in data.get("message", "")
