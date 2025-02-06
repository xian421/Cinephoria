import pytest
import importlib
from unittest import mock
import json
from cinephoria_backend.app import app
from cinephoria_backend.routes.paypal import get_paypal_access_token, capture_paypal_order

# 🔹 Test für `get_paypal_access_token`
@mock.patch("requests.post")
def test_get_paypal_access_token(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"access_token": "test_access_token"}

    access_token = get_paypal_access_token()

    assert access_token == "test_access_token"
    mock_post.assert_called_once()  # Überprüft, dass genau einmal eine Anfrage gesendet wurde.

# 🔹 Test für `create_paypal_order`
@mock.patch("cinephoria_backend.routes.paypal.get_paypal_access_token", return_value="test_access_token")
@mock.patch("requests.post")
def test_create_paypal_order(mock_post, mock_get_token):
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {"id": "test_order_id"}

    client = app.test_client()
    response = client.post("/paypal/create-order", json={"total_amount": "50.00"})

    assert response.status_code == 200
    assert response.get_json() == {"orderID": "test_order_id"}
    mock_post.assert_called_once()
    mock_get_token.assert_called_once()  # Prüft, ob der Token-Mock aufgerufen wurde

# 🔹 Test für `capture_paypal_order`
@mock.patch("cinephoria_backend.routes.paypal.get_paypal_access_token", return_value="test_access_token")
@mock.patch("requests.post")
# Hier patchen wir get_db_connection an der Stelle, an der es in paypal.py genutzt wird:
@mock.patch("cinephoria_backend.routes.paypal.get_db_connection")
@mock.patch("cinephoria_backend.routes.auth.token_optional")
def test_capture_paypal_order(mock_token_optional, mock_get_db_connection, mock_post, mock_get_token):
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {"status": "COMPLETED"}

    # Erstelle einen MagicMock für die Datenbankverbindung, um den Kontextmanager korrekt zu simulieren
    mock_conn = mock.MagicMock()
    mock_conn.__enter__.return_value = mock_conn

    # Erstelle einen MagicMock für den Cursor
    mock_cursor = mock.MagicMock()
    mock_cursor.fetchone.return_value = [123]
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    mock_get_db_connection.return_value = mock_conn  # Setzt den Mock für die DB-Verbindung

    # Token-Decorator so konfigurieren, dass er einfach den Request zurückgibt
    mock_token_optional.return_value = lambda x: x

    client = app.test_client()
    response = client.post("/paypal/capture-order", json={
        "orderID": "test_order_id",
        "vorname": "Max",
        "nachname": "Mustermann",
        "email": "test@example.com",
        "total_amount": "50.00",
        "cart_items": [{"seat_id": 1, "showtime_id": 2, "seat_type_discount_id": None}]
    })

    assert response.status_code == 200
    assert "booking_id" in response.get_json()
    mock_post.assert_called_once()
    mock_get_db_connection.assert_called_once()
    mock_get_token.assert_called_once()
