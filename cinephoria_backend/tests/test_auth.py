import os
os.environ["SECRET_KEY"] = "testsecret"

import pytest
import json
from unittest import mock
from datetime import datetime, timedelta, timezone
import jwt

from cinephoria_backend.app import app
from cinephoria_backend.config import SECRET_KEY

# Hilfsfunktion, um einen Fake-Datenbankkontextmanager zu erstellen
def fake_db_connection():
    conn = mock.MagicMock()
    cursor = mock.MagicMock()
    conn.__enter__.return_value = conn
    conn.cursor.return_value.__enter__.return_value = cursor
    return conn, cursor

@mock.patch("cinephoria_backend.routes.auth.get_db_connection")
def test_login_success(mock_get_db_connection):
    # Simuliere DB-Verbindung und Cursor
    conn, cursor = fake_db_connection()
    mock_get_db_connection.return_value = conn

    # Erster Aufruf: SELECT id, password, vorname, nachname, role FROM users WHERE email = %s
    # Zweiter Aufruf: SELECT crypt(%s, %s) = %s AS password_match
    cursor.fetchone.side_effect = [
        (1, "hashed_password", "Max", "Mustermann", "user"),
        [True]
    ]

    # Erstelle ein Fake-Payload für den Login
    payload = {"email": "test@example.com", "password": "password"}
    client = app.test_client()
    response = client.post("/login", json=payload)

    data = response.get_json()
    assert response.status_code == 200
    assert "token" in data
    # Überprüfe z. B. den Inhalt des Tokens:
    decoded = jwt.decode(data["token"], SECRET_KEY, algorithms=["HS256"])
    assert decoded["user_id"] == 1
    assert decoded["first_name"] == "Max"

@mock.patch("cinephoria_backend.routes.auth.get_db_connection")
def test_login_invalid_user(mock_get_db_connection):
    conn, cursor = fake_db_connection()
    mock_get_db_connection.return_value = conn

    # Kein Ergebnis aus der Datenbank
    cursor.fetchone.return_value = None

    payload = {"email": "nichtvorhanden@example.com", "password": "password"}
    client = app.test_client()
    response = client.post("/login", json=payload)
    data = response.get_json()

    assert response.status_code == 401
    assert "error" in data
