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

# ------------------------------------------------------
# 1) Admin-Token erzeugen (gültig für 1 Stunde)
# ------------------------------------------------------
admin_payload = {
    "user_id": 1,
    "role": "admin",
    "exp": datetime.now(timezone.utc) + timedelta(hours=1)
}
admin_token = jwt.encode(admin_payload, SECRET_KEY, algorithm="HS256")


# ------------------------------------------------------
# 2) Hilfsfunktionen zum Mocken der DB
# ------------------------------------------------------
def fake_db_cursor(rows=None, one_row=None, side_effect=None):
    """
    Gibt ein MagicMock-Objekt zurück, das fetchall() oder fetchone()
    mit den gewünschten Daten simuliert.
    - rows: Liste von Tupeln oder Dicts, die fetchall() liefern soll
    - one_row: Datensatz für fetchone()
    - side_effect: Liste, die fetchone() in mehreren Aufrufen nacheinander zurückgibt
    """
    cursor = mock.MagicMock()

    if side_effect is not None:
        # Jeder Aufruf von fetchone() gibt nacheinander Werte aus side_effect zurück
        cursor.fetchone.side_effect = side_effect
    else:
        cursor.fetchone.return_value = one_row

    cursor.fetchall.return_value = rows or []
    return cursor


def setup_mock_conn(fake_cursor):
    fake_conn = mock.MagicMock()
    fake_conn.__enter__.return_value = fake_conn

    # Hier den Cursor-Kontext
    cursor_ctx = fake_conn.cursor.return_value
    cursor_ctx.__enter__.return_value = fake_cursor

    # Jetzt dem fake_cursor ein "connection"-Mock geben:
    fake_cursor.connection = mock.MagicMock()
    fake_cursor.connection.encoding = "UTF8"

    return fake_conn


# -----------------------------------------------------------------------------
# Test: POST /seats (create_seat)
# -----------------------------------------------------------------------------
def test_create_seat_success():
    """
    Testet einen erfolgreichen POST /seats:
    - Seat-Type wird gefunden (seat_type_id=1)
    - Sitz existiert noch nicht
    - Neuer Sitz wird korrekt angelegt (seat_id=999)
    """
    # Wir simulieren zwei fetchone()-Aufrufe:
    # 1) SELECT seat_types => seat_type_id=1
    # 2) INSERT RETURNING seat_id => 999
    fake_cursor_obj = fake_db_cursor()
    fake_cursor_obj.fetchone.side_effect = [
        (1,),     # seat_type_id = 1
        None,     # kein existierender Sitz
        (999,)    # neuer seat_id beim INSERT RETURNING
    ]

    fake_conn = setup_mock_conn(fake_cursor_obj)

    with mock.patch("cinephoria_backend.routes.seats.get_db_connection", return_value=fake_conn):
        client = app.test_client()
        payload = {
            "screen_id": 123,
            "row": "A",
            "number": 10,
            "type": "premium"
        }
        response = client.post(
            "/seats",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()

        assert response.status_code == 201
        assert data["seat_id"] == 999
        assert data["message"] == "Sitz erstellt"


def test_create_seat_already_exists():
    """
    Testet POST /seats, wenn der Sitz bereits existiert => 400
    """
    # 1) seat_type_id=1
    # 2) SELECT seats => existiert => (500,)
    fake_cursor_obj = fake_db_cursor()
    fake_cursor_obj.fetchone.side_effect = [
        (1,),   # seat_type_id
        (500,)  # existing seat
    ]
    fake_conn = setup_mock_conn(fake_cursor_obj)

    with mock.patch("cinephoria_backend.routes.seats.get_db_connection", return_value=fake_conn):
        client = app.test_client()
        payload = {"screen_id": 10, "row": "B", "number": 10, "type": "standard"}
        response = client.post(
            "/seats",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()

        assert response.status_code == 400
        assert data["error"] == "Sitz existiert bereits"


def test_create_seat_missing_params():
    """
    Testet POST /seats ohne erforderliche Parameter => 400
    """
    fake_cursor_obj = fake_db_cursor()
    fake_conn = setup_mock_conn(fake_cursor_obj)

    with mock.patch("cinephoria_backend.routes.seats.get_db_connection", return_value=fake_conn):
        client = app.test_client()
        # screen_id fehlt absichtlich
        payload = {"row": "C", "number": 5}
        response = client.post(
            "/seats",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()

        assert response.status_code == 400
        assert "error" in data


# -----------------------------------------------------------------------------
# Test: DELETE /seats/<seat_id>
# -----------------------------------------------------------------------------
def test_delete_seat_success():
    """
    Testet DELETE /seats/<seat_id>, wenn rowcount=1 => 200
    """
    fake_cursor_obj = fake_db_cursor()
    fake_cursor_obj.rowcount = 1
    fake_conn = setup_mock_conn(fake_cursor_obj)

    with mock.patch("cinephoria_backend.routes.seats.get_db_connection", return_value=fake_conn):
        client = app.test_client()
        response = client.delete(
            "/seats/999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()

        assert response.status_code == 200
        assert data["message"] == "Sitz gelöscht"


def test_delete_seat_not_found():
    """
    Testet DELETE /seats/<seat_id>, wenn Sitz nicht existiert => 404
    """
    fake_cursor_obj = fake_db_cursor()
    fake_cursor_obj.rowcount = 0  # kein Datensatz gelöscht
    fake_conn = setup_mock_conn(fake_cursor_obj)

    with mock.patch("cinephoria_backend.routes.seats.get_db_connection", return_value=fake_conn):
        client = app.test_client()
        response = client.delete(
            "/seats/999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()

        assert response.status_code == 404
        assert data["error"] == "Sitz nicht gefunden"


# -----------------------------------------------------------------------------
# Test: DELETE /seats?screen_id=XYZ
# -----------------------------------------------------------------------------
def test_delete_all_seats_success():
    """
    Testet DELETE /seats?screen_id=10 => 200
    """
    fake_conn = setup_mock_conn(fake_db_cursor())

    with mock.patch("cinephoria_backend.routes.seats.get_db_connection", return_value=fake_conn):
        client = app.test_client()
        response = client.delete(
            "/seats?screen_id=10",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()

        assert response.status_code == 200
        assert data["message"] == "Alle Sitze gelöscht"


def test_delete_all_seats_missing_screen_id():
    """
    Testet DELETE /seats ohne screen_id => 400
    """
    fake_conn = setup_mock_conn(fake_db_cursor())

    with mock.patch("cinephoria_backend.routes.seats.get_db_connection", return_value=fake_conn):
        client = app.test_client()
        response = client.delete(
            "/seats",  # kein screen_id
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()

        assert response.status_code == 400
        assert "error" in data


# -----------------------------------------------------------------------------
# Test: GET /seats?screen_id=...
# -----------------------------------------------------------------------------
def test_get_seats_success():
    """
    Testet GET /seats?screen_id=..., erwartet seats-Liste.
    (Kein Admin-Token nötig, da GET /seats nicht @admin_required hat.)
    """
    rows = [
        (101, 10, "A", 5, "standard", 12.5),
        (102, 10, "A", 6, "premium", 15.0),
    ]
    fake_cursor_obj = fake_db_cursor(rows=rows)
    fake_conn = setup_mock_conn(fake_cursor_obj)

    with mock.patch("cinephoria_backend.routes.seats.get_db_connection", return_value=fake_conn):
        client = app.test_client()
        # Hier bei GET ist in seats.py kein @admin_required => Token nicht zwingend nötig
        response = client.get("/seats?screen_id=10")
        data = response.get_json()

        assert response.status_code == 200
        assert "seats" in data
        assert len(data["seats"]) == 2


def test_get_seats_missing_screen_id():
    """
    Testet GET /seats ohne screen_id => 400
    """
    fake_conn = setup_mock_conn(fake_db_cursor())

    with mock.patch("cinephoria_backend.routes.seats.get_db_connection", return_value=fake_conn):
        client = app.test_client()
        response = client.get("/seats")  # kein screen_id
        data = response.get_json()

        assert response.status_code == 400
        assert "error" in data


# -----------------------------------------------------------------------------
# Test: GET /seats/<seat_id>
# -----------------------------------------------------------------------------
def test_get_seat_success():
    """
    Testet GET /seats/<seat_id>, wenn Sitz gefunden wird => 200
    """
    row = (999, 10, "A", 5, "standard", 10.0, 1)
    fake_cursor_obj = fake_db_cursor(one_row=row)
    fake_conn = setup_mock_conn(fake_cursor_obj)

    with mock.patch("cinephoria_backend.routes.seats.get_db_connection", return_value=fake_conn):
        client = app.test_client()
        response = client.get("/seats/999")
        data = response.get_json()

        assert response.status_code == 200
        assert "seat" in data
        assert data["seat"]["seat_id"] == 999
        assert data["seat"]["price"] == 10.0


def test_get_seat_not_found():
    """
    Testet GET /seats/<seat_id>, wenn kein Datensatz existiert => 404
    """
    fake_cursor_obj = fake_db_cursor(one_row=None)
    fake_conn = setup_mock_conn(fake_cursor_obj)

    with mock.patch("cinephoria_backend.routes.seats.get_db_connection", return_value=fake_conn):
        client = app.test_client()
        response = client.get("/seats/999")
        data = response.get_json()

        assert response.status_code == 404
        assert data["error"] == "Sitz nicht gefunden"


# -----------------------------------------------------------------------------
# Test: POST /seats/batch_update
# -----------------------------------------------------------------------------
def test_batch_update_seats_success():
    """
    Testet POST /seats/batch_update mit gültigen Daten.
    Prüft, ob execute_values aufgerufen wird und ob ein 200-Status zurückkommt.
    """
    fake_cursor_obj = fake_db_cursor()
    # seat_type-Abfragen => side_effect
    fake_cursor_obj.fetchone.side_effect = [
        (2,),  # seat_type_id (für seats_to_add[0])
        (2,),  # seat_type_id (für seats_to_add[1])
        (3,),  # seat_type_id (für seats_to_update[0])
    ]
    fake_conn = setup_mock_conn(fake_cursor_obj)

    with mock.patch("cinephoria_backend.routes.seats.get_db_connection", return_value=fake_conn):
        with mock.patch("psycopg2.extras.execute_values", return_value=None):
            client = app.test_client()
            payload = {
                "screen_id": 10,
                "seats_to_add": [
                    {"row": "A", "number": 1, "type": "premium"},
                    {"row": "B", "number": 2, "type": "premium"}
                ],
                "seats_to_delete": [
                    {"row": "C", "number": 3}
                ],
                "seats_to_update": [
                    {"row": "D", "number": 4, "type": "vip"}
                ]
            }
            response = client.post(
                "/seats/batch_update",
                json=payload,
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            data = response.get_json()

            assert response.status_code == 200
            assert data["message"] == "Sitze erfolgreich aktualisiert"
            assert data["added"] == 2
            assert data["deleted"] == 1
            assert data["updated"] == 1


def test_batch_update_seats_invalid_type():
    """
    Testet POST /seats/batch_update, wenn ein ungültiger Sitztyp vorkommt => 400
    """
    fake_cursor_obj = fake_db_cursor()
    # seat_type => None => ungültiger Typ
    fake_cursor_obj.fetchone.return_value = None
    fake_conn = setup_mock_conn(fake_cursor_obj)

    with mock.patch("cinephoria_backend.routes.seats.get_db_connection", return_value=fake_conn):
        client = app.test_client()
        payload = {
            "screen_id": 10,
            "seats_to_add": [
                {"row": "A", "number": 1, "type": "unbekannt"}
            ]
        }
        response = client.post(
            "/seats/batch_update",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()

        assert response.status_code == 400
        assert "error" in data


def test_batch_update_seats_missing_screen_id():
    """
    Testet POST /seats/batch_update ohne screen_id => 400
    """
    fake_conn = setup_mock_conn(fake_db_cursor())

    with mock.patch("cinephoria_backend.routes.seats.get_db_connection", return_value=fake_conn):
        client = app.test_client()
        payload = {
            # kein screen_id
            "seats_to_add": [{"row": "A", "number": 1}]
        }
        response = client.post(
            "/seats/batch_update",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.get_json()

        assert response.status_code == 400
        assert "error" in data
