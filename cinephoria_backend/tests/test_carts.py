import os
os.environ["SECRET_KEY"] = "testsecret"  # Muss vor allen Importen gesetzt werden!

import json
from datetime import datetime, timedelta, timezone
from unittest import mock
import pytest
import psycopg2.extras
import jwt

from cinephoria_backend.app import app
from cinephoria_backend.config import SECRET_KEY

# Erzeuge einen gültigen User-Token für user_cart-Endpunkte
user_payload = {
    "user_id": 20,
    "role": "user",
    "exp": datetime.now(timezone.utc) + timedelta(hours=1)
}
user_token = jwt.encode(user_payload, SECRET_KEY, algorithm="HS256")

# Hilfsfunktion: Fake-DB-Kontextmanager, der einen übergebenen Cursor liefert
def fake_db_conn(cursor):
    conn = mock.MagicMock()
    conn.__enter__.return_value = conn
    conn.cursor.return_value.__enter__.return_value = cursor
    return conn

#############################################
# Tests für Guest-Cart (guestcart.py)
#############################################

# GET /guest/cart: Test, wenn kein Eintrag existiert (Neuanlage)
def test_guest_cart_get_new():
    guest_id = "guest123"
    # Simuliere: SELECT guest_id, valid_until gibt zunächst nichts zurück
    cursor = mock.MagicMock()
    # Erstes fetchone() (für den Warenkorb) liefert None
    cursor.fetchone.side_effect = [None,  # SELECT guest cart -> None
                                   ] 
    # Danach wird für Items fetchall() aufgerufen – simulieren wir leere Liste
    cursor.fetchall.return_value = []
    conn = fake_db_conn(cursor)
    
    with mock.patch("cinephoria_backend.routes.guestcart.get_db_connection", return_value=conn):
        client = app.test_client()
        response = client.get(f"/guest/cart?guest_id={guest_id}")
        data = response.get_json()
        # Wir erwarten einen 200-Status, einen valid_until-Wert (als ISO-String) und leere cart_items
        assert response.status_code == 200
        assert "valid_until" in data
        assert data["cart_items"] == []

# GET /guest/cart: Test, wenn ein Eintrag bereits existiert (mit gültigem valid_until)
def test_guest_cart_get_existing():
    guest_id = "guest456"
    valid_until = datetime.now(timezone.utc) + timedelta(minutes=15)
    # Simuliere einen vorhandenen Warenkorb (als Dict-like Objekt)
    fake_cart = {"guest_id": guest_id, "valid_until": valid_until}
    cursor = mock.MagicMock()
    # Hier liefert der erste fetchone() das Fake-Cart als dict
    cursor.fetchone.return_value = fake_cart
    # Für Items liefern wir z. B. zwei Einträge
    fake_items = [
        {
            "seat_id": 101,
            "price": 12.50,
            "reserved_until": datetime.now(timezone.utc) + timedelta(minutes=15),
            "showtime_id": 300,
            "seat_type_discount_id": None
        },
        {
            "seat_id": 102,
            "price": 12.50,
            "reserved_until": datetime.now(timezone.utc) + timedelta(minutes=15),
            "showtime_id": 300,
            "seat_type_discount_id": 5
        }
    ]
    cursor.fetchall.return_value = fake_items
    conn = fake_db_conn(cursor)
    
    with mock.patch("cinephoria_backend.routes.guestcart.get_db_connection", return_value=conn):
        client = app.test_client()
        response = client.get(f"/guest/cart?guest_id={guest_id}")
        data = response.get_json()
        assert response.status_code == 200
        # Es sollten zwei Items zurückgegeben werden
        assert isinstance(data["cart_items"], list)
        assert len(data["cart_items"]) == 2

# POST /guest/cart: Sitz zum Guest-Warenkorb hinzufügen
def test_guest_cart_post_success():
    guest_id = "guest789"
    seat_id = 201
    price = 15.0
    showtime_id = 400
    seat_type_discount_id = None
    # Wir simulieren: Zuerst SELECT guest_cart -> kein Eintrag, dann INSERT in guest_carts
    # Dann: SELECT seat_id from user_cart_items -> gibt None zurück (kein Konflikt)
    # Anschließend: INSERT in guest_cart_items liefert RETURNING seat_id
    cursor = mock.MagicMock()
    cursor.fetchone.side_effect = [
        None,  # SELECT guest_cart -> None
        None,  # SELECT seat_id from user_cart_items -> None (kein Reservierungs-Konflikt)
        (seat_id,),  # INSERT INTO guest_cart_items -> RETURNING seat_id
    ]
    cursor.fetchall.return_value = []  # für eventuelle Items-Abfrage
    conn = fake_db_conn(cursor)
    
    with mock.patch("cinephoria_backend.routes.guestcart.get_db_connection", return_value=conn):
        client = app.test_client()
        payload = {
            "guest_id": guest_id,
            "seat_id": seat_id,
            "price": price,
            "showtime_id": showtime_id,
            "seat_type_discount_id": seat_type_discount_id
        }
        response = client.post("/guest/cart", json=payload)
        data = response.get_json()
        assert response.status_code == 201
        assert "Sitzplatz zum Guest-Warenkorb hinzugefügt" in data.get("message", "")
        assert "reserved_until" in data

# DELETE /guest/cart/<int:showtime_id>/<int:seat_id>: Ein einzelnes Item entfernen
def test_guest_cart_delete_item_success():
    guest_id = "guestABC"
    seat_id = 301
    showtime_id = 500
    cursor = mock.MagicMock()
    # Wir simulieren, dass das Update und der DELETE erfolgreich sind.
    conn = fake_db_conn(cursor)
    
    with mock.patch("cinephoria_backend.routes.guestcart.get_db_connection", return_value=conn):
        client = app.test_client()
        response = client.delete(f"/guest/cart/{showtime_id}/{seat_id}?guest_id={guest_id}")
        data = response.get_json()
        assert response.status_code == 200
        assert "Sitzplatz aus dem Guest-Warenkorb entfernt" in data.get("message", "")

# DELETE /guest/cart: Den gesamten Guest-Warenkorb leeren
def test_guest_cart_clear_success():
    guest_id = "guestXYZ"
    cursor = mock.MagicMock()
    conn = fake_db_conn(cursor)
    
    with mock.patch("cinephoria_backend.routes.guestcart.get_db_connection", return_value=conn):
        client = app.test_client()
        response = client.delete(f"/guest/cart?guest_id={guest_id}")
        data = response.get_json()
        assert response.status_code == 200
        assert "Guest-Warenkorb geleert" in data.get("message", "")

# POST /guest/cart/update: Update eines Cart-Items (z. B. Discount setzen)
def test_guest_cart_update_success():
    guest_id = "guestUPDATE"
    seat_id = 401
    showtime_id = 600
    new_discount = 7  # Beispielwert
    # Simuliere, dass das Item existiert und die Validierung erfolgreich ist
    fake_cart_item = (55, None)  # z. B. cart_item_id = 55
    cursor = mock.MagicMock()
    cursor.fetchone.side_effect = [
        fake_cart_item,      # SELECT cart_item_id, seat_type_discount_id FROM guest_cart_items ...
        (1,),                # SELECT 1 FROM seat_type_discounts ... (Validierung erfolgreich)
    ]
    conn = fake_db_conn(cursor)
    
    with mock.patch("cinephoria_backend.routes.guestcart.get_db_connection", return_value=conn):
        client = app.test_client()
        payload = {
            "guest_id": guest_id,
            "seat_id": seat_id,
            "showtime_id": showtime_id,
            "seat_type_discount_id": new_discount
        }
        response = client.post("/guest/cart/update", json=payload)
        data = response.get_json()
        assert response.status_code == 200
        assert "Gast-Warenkorb erfolgreich aktualisiert" in data.get("message", "")

#############################################
# Tests für User-Cart (usercart.py)
#############################################

# GET /user/cart: Test, wenn kein Warenkorb existiert (Neuanlage)
def test_user_cart_get_new():
    user_id = 20  # Dieser Wert wird aus dem Token (user_token) übernommen
    cursor = mock.MagicMock()
    # Erster fetchone() liefert None, danach fetchall() leere Liste
    cursor.fetchone.side_effect = [None]
    cursor.fetchall.return_value = []
    conn = fake_db_conn(cursor)
    
    with mock.patch("cinephoria_backend.routes.usercart.get_db_connection", return_value=conn):
        client = app.test_client()
        response = client.get("/user/cart", headers={"Authorization": f"Bearer {user_token}"})
        data = response.get_json()
        assert response.status_code == 200
        assert "valid_until" in data
        assert data["cart_items"] == []

# DELETE /user/cart/<int:showtime_id>/<int:seat_id>: Ein Item entfernen
def test_user_cart_delete_item_success():
    user_id = 20
    showtime_id = 700
    seat_id = 501
    cursor = mock.MagicMock()
    conn = fake_db_conn(cursor)
    
    with mock.patch("cinephoria_backend.routes.usercart.get_db_connection", return_value=conn):
        client = app.test_client()
        response = client.delete(f"/user/cart/{showtime_id}/{seat_id}", headers={"Authorization": f"Bearer {user_token}"})
        data = response.get_json()
        assert response.status_code == 200
        assert "Sitzplatz aus dem Warenkorb entfernt" in data.get("message", "")

# DELETE /user/cart: Den gesamten Warenkorb leeren
def test_user_cart_clear_success():
    user_id = 20
    cursor = mock.MagicMock()
    conn = fake_db_conn(cursor)
    
    with mock.patch("cinephoria_backend.routes.usercart.get_db_connection", return_value=conn):
        client = app.test_client()
        response = client.delete("/user/cart", headers={"Authorization": f"Bearer {user_token}"})
        data = response.get_json()
        assert response.status_code == 200
        assert "Warenkorb geleert" in data.get("message", "")

# POST /user/cart: Ein Item zum Warenkorb hinzufügen
def test_user_cart_post_success():
    user_id = 20
    seat_id = 601
    price = 18.0
    showtime_id = 800
    seat_type_discount_id = None
    cursor = mock.MagicMock()
    # Simuliere: SELECT user_cart (None) -> INSERT, dann SELECT in guest_cart_items -> None, danach INSERT in user_cart_items liefert RETURNING seat_id
    cursor.fetchone.side_effect = [
        None,     # SELECT user_carts -> None
        None,     # SELECT seat_id FROM guest_cart_items -> None (kein Konflikt)
        (seat_id,)  # INSERT in user_cart_items -> RETURNING seat_id
    ]
    conn = fake_db_conn(cursor)
    
    with mock.patch("cinephoria_backend.routes.usercart.get_db_connection", return_value=conn):
        client = app.test_client()
        payload = {
            "seat_id": seat_id,
            "price": price,
            "showtime_id": showtime_id,
            "seat_type_discount_id": seat_type_discount_id
        }
        response = client.post("/user/cart", json=payload, headers={"Authorization": f"Bearer {user_token}"})
        data = response.get_json()
        assert response.status_code == 201
        assert "Sitzplatz zum Warenkorb hinzugefügt" in data.get("message", "")
        assert "reserved_until" in data

# POST /user/cart/update: Update eines Items im Warenkorb
def test_user_cart_update_success():
    user_id = 20
    seat_id = 701
    showtime_id = 900
    new_discount = 9
    # Simuliere, dass das Item existiert: Rückgabe von (cart_item_id, current_discount)
    fake_cart_item = (77, None)
    cursor = mock.MagicMock()
    # Zuerst SELECT cart_item; danach SELECT zur Validierung des Discounts liefert (1,)
    cursor.fetchone.side_effect = [
        fake_cart_item,
        (1,)
    ]
    conn = fake_db_conn(cursor)
    
    with mock.patch("cinephoria_backend.routes.usercart.get_db_connection", return_value=conn):
        client = app.test_client()
        payload = {
            "seat_id": seat_id,
            "showtime_id": showtime_id,
            "seat_type_discount_id": new_discount
        }
        response = client.post("/user/cart/update", json=payload, headers={"Authorization": f"Bearer {user_token}"})
        data = response.get_json()
        assert response.status_code == 200
        assert "Warenkorb erfolgreich aktualisiert" in data.get("message", "")

