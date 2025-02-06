import os
os.environ["SECRET_KEY"] = "testsecret"  # Muss vor allen Importen gesetzt werden!

import json
import pytest
from unittest import mock
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta, timezone
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

# 1. GET /discounts
def test_get_discounts_success():
    fake_discounts = [
        {"discount_id": 1, "name": "Discount A", "description": "Desc A"},
        {"discount_id": 2, "name": "Discount B", "description": "Desc B"}
    ]
    # Simuliere einen DB-Kontextmanager, der fetchall() liefert
    conn = mock.MagicMock()
    cursor = mock.MagicMock()
    cursor.fetchall.return_value = fake_discounts
    conn.__enter__.return_value = conn
    conn.cursor.return_value.__enter__.return_value = cursor

    with mock.patch("cinephoria_backend.routes.discounts.get_db_connection", return_value=conn):
        client = app.test_client()
        response = client.get("/discounts")
        data = response.get_json()

        assert response.status_code == 200
        assert "discounts" in data
        assert len(data["discounts"]) == 2

# 2. POST /discounts (Discount hinzufügen)
def test_add_discount_success():
    # Simuliere einen DB-Kontextmanager für den Insert
    conn = mock.MagicMock()
    cursor = mock.MagicMock()
    # Der Cursor liefert beim INSERT einen neuen discount_id zurück
    cursor.fetchone.return_value = [123]
    conn.__enter__.return_value = conn
    conn.cursor.return_value.__enter__.return_value = cursor

    with mock.patch("cinephoria_backend.routes.discounts.get_db_connection", return_value=conn):
        client = app.test_client()
        payload = {"name": "Test Discount", "description": "Test Beschreibung"}
        response = client.post(
            "/discounts",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()

        # Wir erwarten hier einen 201-Status, da der Insert erfolgreich war.
        assert response.status_code == 201
        assert data.get("discount_id") == 123

# 3. PUT /discounts/<int:discount_id> (Discount aktualisieren)
def test_update_discount_success():
    conn = mock.MagicMock()
    cursor = mock.MagicMock()
    # Simuliere, dass ein Update tatsächlich erfolgte (rowcount > 0)
    cursor.rowcount = 1
    conn.__enter__.return_value = conn
    conn.cursor.return_value.__enter__.return_value = cursor

    with mock.patch("cinephoria_backend.routes.discounts.get_db_connection", return_value=conn):
        client = app.test_client()
        discount_id = 1
        payload = {"name": "Updated Discount", "description": "Updated Beschreibung"}
        response = client.put(
            f"/discounts/{discount_id}",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()

        assert response.status_code == 200
        assert data.get("message") == "Discount aktualisiert"

# 4. DELETE /discounts/<int:discount_id> (Discount löschen)
def test_delete_discount_success():
    conn = mock.MagicMock()
    cursor = mock.MagicMock()
    # Simuliere, dass der Löschvorgang einen Datensatz entfernt (rowcount > 0)
    cursor.rowcount = 1
    conn.__enter__.return_value = conn
    conn.cursor.return_value.__enter__.return_value = cursor

    with mock.patch("cinephoria_backend.routes.discounts.get_db_connection", return_value=conn):
        client = app.test_client()
        discount_id = 1
        response = client.delete(
            f"/discounts/{discount_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()

        assert response.status_code == 200
        assert data.get("message") == "Discount gelöscht"

# 5. POST /seat_type_discounts (Discount einem Sitztyp zuweisen)
def test_assign_discount_to_seat_type_success():
    conn = mock.MagicMock()
    cursor = mock.MagicMock()
    # Simuliere, dass die Abfragen für seat_type und discount existieren:
    # Erster fetchone-Aufruf: seat_type existiert; zweiter: discount existiert
    cursor.fetchone.side_effect = [(1,), (1,)]
    conn.__enter__.return_value = conn
    conn.cursor.return_value.__enter__.return_value = cursor

    with mock.patch("cinephoria_backend.routes.discounts.get_db_connection", return_value=conn):
        client = app.test_client()
        payload = {
            "seat_type_id": 1,
            "discount_id": 2,
            "discount_amount": 5,
            "discount_percentage": None
        }
        response = client.post(
            "/seat_type_discounts",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()

        assert response.status_code == 200
        assert data.get("message") == "Discount dem Sitztyp zugewiesen"

# 6. DELETE /seat_type_discounts (Discount von einem Sitztyp entfernen)
def test_remove_discount_from_seat_type_success():
    conn = mock.MagicMock()
    cursor = mock.MagicMock()
    # Simuliere, dass das DELETE einen Eintrag entfernt (rowcount > 0)
    cursor.rowcount = 1
    conn.__enter__.return_value = conn
    conn.cursor.return_value.__enter__.return_value = cursor

    with mock.patch("cinephoria_backend.routes.discounts.get_db_connection", return_value=conn):
        client = app.test_client()
        payload = {"seat_type_id": 1, "discount_id": 2}
        response = client.delete(
            "/seat_type_discounts",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()

        assert response.status_code == 200
        assert data.get("message") == "Discount vom Sitztyp entfernt"

# 7. GET /seat_types_with_discounts
def test_get_seat_types_with_discounts_success():
    # Simuliere DB-Ergebnis: zwei Sitztypen, einer ohne, einer mit Discount
    fake_results = [
        {
            "seat_type_id": 1,
            "seat_type_name": "Normal",
            "price": 10.0,
            "color": "blue",
            "icon": "icon.png",
            "discount_id": None,
            "discount_name": None,
            "description": None,
            "discount_amount": None,
            "discount_percentage": None,
            "seat_type_discount_id": None
        },
        {
            "seat_type_id": 2,
            "seat_type_name": "VIP",
            "price": 20.0,
            "color": "red",
            "icon": "vip.png",
            "discount_id": 1,
            "discount_name": "VIP Rabatt",
            "description": "Rabatt für VIPs",
            "discount_amount": 5,
            "discount_percentage": None,
            "seat_type_discount_id": 10
        }
    ]
    conn = mock.MagicMock()
    cursor = mock.MagicMock()
    cursor.fetchall.return_value = fake_results
    conn.__enter__.return_value = conn
    conn.cursor.return_value.__enter__.return_value = cursor

    with mock.patch("cinephoria_backend.routes.discounts.get_db_connection", return_value=conn):
        client = app.test_client()
        response = client.get("/seat_types_with_discounts")
        data = response.get_json()

        assert response.status_code == 200
        assert "seat_types" in data
        assert isinstance(data["seat_types"], list)
        # Überprüfe, dass der VIP-Sitztyp einen Discount enthält
        vip = next((st for st in data["seat_types"] if st["seat_type_id"] == 2), None)
        assert vip is not None
        assert len(vip["discounts"]) == 1

# 8. GET /discount/<int:seat_type_id>
def test_get_discount_for_seat_type_success():
    fake_results = [
        {
            "discount_id": 1,
            "seat_type_discount_id": 10,
            "discount_name": "VIP Rabatt",
            "description": "Rabatt für VIPs",
            "discount_amount": 5,
            "discount_percentage": None
        }
    ]
    conn = mock.MagicMock()
    cursor = mock.MagicMock()
    cursor.fetchall.return_value = fake_results
    conn.__enter__.return_value = conn
    conn.cursor.return_value.__enter__.return_value = cursor

    with mock.patch("cinephoria_backend.routes.discounts.get_db_connection", return_value=conn):
        client = app.test_client()
        response = client.get("/discount/2")
        data = response.get_json()

        assert response.status_code == 200
        assert "discounts" in data
        assert len(data["discounts"]) == 1
        # Prüfe, ob der Name des Discounts stimmt (basierend auf fake_results)
        assert data["discounts"][0]["name"] == "VIP Rabatt"
