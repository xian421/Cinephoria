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

# Hilfsfunktion für Fake-DB-Kontextmanager
def fake_db_conn(return_values, fetchall_return=[]):
    """
    return_values: Liste von Werten, die nacheinander von fetchone() geliefert werden.
    fetchall_return: Wert, den fetchall() zurückgibt.
    """
    conn = mock.MagicMock()
    cursor = mock.MagicMock()
    cursor.fetchone.side_effect = return_values
    cursor.fetchall.return_value = fetchall_return
    conn.__enter__.return_value = conn
    conn.cursor.return_value.__enter__.return_value = cursor
    return conn

#############################################
# Tests für die Sitztypen-Routen
#############################################

# Test für GET /seat_types
def test_get_seat_types_success():
    # Simuliere DB-Ergebnis: Zwei Sitztypen als Tupel:
    # (seat_type_id, name, price, color, icon)
    fake_rows = [
        (1, "Standard", 10.0, "blue", "icon-standard"),
        (2, "VIP", 20.0, None, "icon-vip")
    ]
    conn = fake_db_conn(return_values=[], fetchall_return=fake_rows)
    with mock.patch("cinephoria_backend.routes.seat_types.get_db_connection", return_value=conn):
        client = app.test_client()
        response = client.get("/seat_types")
        data = response.get_json()
        assert response.status_code == 200
        assert "seat_types" in data
        assert isinstance(data["seat_types"], list)
        assert len(data["seat_types"]) == 2
        # Prüfe, ob Default-Farbe gesetzt wird, wenn color None ist (im zweiten Sitztyp)
        vip = next((st for st in data["seat_types"] if st["seat_type_id"] == 2), None)
        assert vip is not None
        assert vip["color"] == "#678be0"

# Test für POST /seat_types (Hinzufügen eines Sitztyps)
def test_add_seat_type_success():
    # Simuliere, dass bei INSERT in die DB ein neuer seat_type_id zurückgegeben wird.
    conn = fake_db_conn(return_values=[(3,)])
    with mock.patch("cinephoria_backend.routes.seat_types.get_db_connection", return_value=conn):
        client = app.test_client()
        payload = {
            "name": "Economy",
            "price": 8.0,
            "color": "green",
            "icon": "icon-economy"
        }
        response = client.post(
            "/seat_types",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()
        # Wir erwarten hier einen 201-Status, da der Insert erfolgreich war.
        assert response.status_code == 201, f"Statuscode: {response.status_code}"
        assert data.get("seat_type_id") == 3

# Test für PUT /seat_types/<int:seat_type_id> (Aktualisieren eines Sitztyps)
def test_update_seat_type_success():
    # Simuliere, dass das UPDATE einen Datensatz aktualisiert (cursor.rowcount > 0)
    conn = fake_db_conn(return_values=[None])
    cursor = conn.cursor.return_value.__enter__.return_value
    cursor.rowcount = 1
    with mock.patch("cinephoria_backend.routes.seat_types.get_db_connection", return_value=conn):
        client = app.test_client()
        payload = {
            "name": "Premium",
            "price": 15.0,
            "color": "purple",
            "icon": "icon-premium"
        }
        response = client.put(
            "/seat_types/2",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()
        assert response.status_code == 200, f"Statuscode: {response.status_code}"
        assert "Sitztyp aktualisiert" in data.get("message", "")

# Test für DELETE /seat_types/<int:seat_type_id> (Löschen eines Sitztyps)
def test_delete_seat_type_success():
    # Simuliere, dass beim DELETE ein Datensatz entfernt wird (cursor.rowcount > 0)
    conn = fake_db_conn(return_values=[None])
    cursor = conn.cursor.return_value.__enter__.return_value
    cursor.rowcount = 1
    with mock.patch("cinephoria_backend.routes.seat_types.get_db_connection", return_value=conn):
        client = app.test_client()
        response = client.delete(
            "/seat_types/2",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()
        assert response.status_code == 200, f"Statuscode: {response.status_code}"
        assert "Sitztyp gelöscht" in data.get("message", "")
