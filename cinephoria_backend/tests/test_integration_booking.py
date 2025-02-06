import os
os.environ["SECRET_KEY"] = "testsecret"  # Muss vor allen Importen gesetzt werden!

import json
import pytest
import jwt
from unittest import mock
from datetime import datetime, timedelta, timezone

from cinephoria_backend.app import app
from cinephoria_backend.config import SECRET_KEY

# Wir bauen uns ein User-Token (role=user)
user_payload = {
    "user_id": 999,  # z.B. user_id 999
    "role": "user",
    "exp": datetime.now(timezone.utc) + timedelta(hours=1)
}
user_token = jwt.encode(user_payload, SECRET_KEY, algorithm="HS256")


##############################################################################
# 1) Abbruch der Zahlung
##############################################################################
@mock.patch("cinephoria_backend.routes.paypal.get_paypal_access_token", return_value="fake_access_token")
@mock.patch("requests.post")
@mock.patch("cinephoria_backend.routes.paypal.get_db_connection")
@mock.patch("cinephoria_backend.routes.usercart.get_db_connection")
@mock.patch("cinephoria_backend.routes.usercart.clear_expired_user_cart_items")
@mock.patch("cinephoria_backend.routes.auth.token_required")
def test_integration_ticket_booking_abort(
    mock_token_required,
    mock_clear_expired,
    mock_db_usercart,
    mock_db_paypal,
    mock_requests_post,
    mock_get_paypal_access_token
):
    """
    Testet den Ablauf:
    1) Sitz in User-Warenkorb hinzufügen.
    2) Nochmal denselben Sitz hinzufügen (soll 409-Fehler geben).
    3) Discount anwenden (Warenkorb-Update).
    4) PayPal-Order erstellen (create-order).
    5) Zahlung "abbrechen" (wir rufen capture-order NICHT auf) => Sitz sollte noch im Warenkorb liegen.
    """

    # ----------------------------------------------------------------------------------
    # (A) DB/Mock-Setup für user_carts
    # ----------------------------------------------------------------------------------
    mock_conn_usercart = mock.MagicMock()
    mock_conn_usercart.__enter__.return_value = mock_conn_usercart
    mock_cursor_usercart = mock.MagicMock()
    mock_conn_usercart.cursor.return_value.__enter__.return_value = mock_cursor_usercart

    # Wir simulieren folgende fetchone()-Aufrufe:
    #
    # 1) POST /user/cart => SELECT user_carts => None => wir legen an
    # 2) POST /user/cart => SELECT seat_id FROM guest_cart_items => None => kein Konflikt
    # 3) POST /user/cart => INSERT => returning seat_id=1 => OK
    #
    # 4) POST (Double-Add) => SELECT user_carts => (1,) => existiert
    # 5) POST (Double-Add) => SELECT seat_id FROM guest_cart_items => None
    # 6) POST (Double-Add) => INSERT => returning seat_id=None => 409
    #
    # 7) POST /user/cart/update => SELECT cart_item_id => (123, None)
    # 8) POST /user/cart/update => SELECT 1 FROM seat_type_discounts => (1,)
    #
    # 9) GET /user/cart => SELECT user_id, valid_until => dict mit valid_until
    #
    mock_cursor_usercart.fetchone.side_effect = [
        None,               # (1)
        None,               # (2)
        (1,),               # (3)
        (1,),               # (4)
        None,               # (5)
        None,               # (6)
        (123, None),        # (7)
        (1,),               # (8)
        {
            "user_id": 999,
            "valid_until": datetime.now(timezone.utc) + timedelta(minutes=15)
        }                   # (9)
    ]

    # Außerdem brauchen wir fetchall() für GET /user/cart => cart_items:
    mock_cursor_usercart.fetchall.return_value = [
        {
            "seat_id": 777,
            "price": 10.0,
            "reserved_until": datetime.now(timezone.utc),
            "showtime_id": 55,
            "seat_type_discount_id": 99
        }
    ]

    mock_db_usercart.return_value = mock_conn_usercart

    # Für PayPal-spezifische DB-Operationen (hier kein capture),
    # d.h. wir werden gar nichts aus der PayPal-DB ändern. Du kannst den Mock minimal halten.
    mock_conn_paypal = mock.MagicMock()
    mock_conn_paypal.__enter__.return_value = mock_conn_paypal
    mock_cursor_paypal = mock.MagicMock()
    mock_conn_paypal.cursor.return_value.__enter__.return_value = mock_cursor_paypal
    mock_db_paypal.return_value = mock_conn_paypal

    # Patch für token_required: wir "umgehen" die Auth-Abfrage und lassen user_id=999 zu
    def token_required_decorator(f):
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapper
    mock_token_required.side_effect = token_required_decorator

    client = app.test_client()

    # ----------------------------------------------------------------------------------
    # (B) Schritt 1: Sitz hinzufügen => 201 OK
    # ----------------------------------------------------------------------------------
    add_payload = {
        "seat_id": 777,
        "price": 10.0,
        "showtime_id": 55,
        "seat_type_discount_id": None
    }
    resp_add = client.post(
        "/user/cart",
        json=add_payload,
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert resp_add.status_code == 201, "Erstes Hinzufügen sollte erfolgreich sein"

    # ----------------------------------------------------------------------------------
    # (C) Schritt 1a: Double-Add => 409 Conflict
    # ----------------------------------------------------------------------------------
    resp_add_again = client.post(
        "/user/cart",
        json=add_payload,
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert resp_add_again.status_code == 409, "Doppeltes Hinzufügen sollte 409 liefern"

    # ----------------------------------------------------------------------------------
    # (D) Schritt 2: Discount anwenden
    # ----------------------------------------------------------------------------------
    update_payload = {
        "seat_id": 777,
        "showtime_id": 55,
        "seat_type_discount_id": 99
    }
    resp_update = client.post(
        "/user/cart/update",
        json=update_payload,
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert resp_update.status_code == 200, "Warenkorb-Update sollte klappen"

    # ----------------------------------------------------------------------------------
    # (E) Schritt 3: PayPal-Order erstellen => 201 => "id": "test_order_id_ABC"
    # ----------------------------------------------------------------------------------
    mock_requests_post.return_value.status_code = 201
    mock_requests_post.return_value.json.return_value = {"id": "test_order_id_ABC"}

    create_order_resp = client.post("/paypal/create-order", json={"total_amount": "10"})
    assert create_order_resp.status_code == 200, "PayPal-Order sollte erfolgreich erstellt werden"
    order_data = create_order_resp.get_json()
    assert order_data.get("orderID") == "test_order_id_ABC"

    # ----------------------------------------------------------------------------------
    # (F) Schritt 3a: Zahlung abbrechen => wir rufen /paypal/capture-order NICHT auf.
    # Stattdessen checken wir, ob der Sitz im Warenkorb bleibt.
    # ----------------------------------------------------------------------------------
    cart_resp = client.get("/user/cart", headers={"Authorization": f"Bearer {user_token}"})
    assert cart_resp.status_code == 200, "Warenkorb sollte abrufbar sein"
    cart_data = cart_resp.get_json()
    seats = cart_data.get("cart_items", [])
    # Sitz sollte noch drin sein:
    assert any(item["seat_id"] == 777 for item in seats), "Sitz muss nach Abbruch noch im Warenkorb sein"


##############################################################################
# 2) Erfolgreiche Zahlung
##############################################################################
@mock.patch("cinephoria_backend.routes.paypal.get_paypal_access_token", return_value="fake_access_token")
@mock.patch("requests.post")
@mock.patch("cinephoria_backend.routes.paypal.get_db_connection")
@mock.patch("cinephoria_backend.routes.usercart.get_db_connection")
@mock.patch("cinephoria_backend.routes.usercart.clear_expired_user_cart_items")
@mock.patch("cinephoria_backend.routes.auth.token_required")
def test_integration_ticket_booking_success(
    mock_token_required,
    mock_clear_expired,
    mock_db_usercart,
    mock_db_paypal,
    mock_requests_post,
    mock_get_paypal_access_token
):
    """
    Testet den Ablauf:
    1) Sitz in User-Warenkorb hinzufügen.
    2) PayPal-Order erstellen (create-order).
    3) PayPal-Order "capturen" => d.h. erfolgreicher Abschluss
    4) Prüfen, ob der Warenkorb geleert und Booking in DB angelegt wurde.
    """

    # ----------------------------------------------------------------------------------
    # (A) DB/Mock-Setup für user_carts
    # ----------------------------------------------------------------------------------
    mock_conn_usercart = mock.MagicMock()
    mock_conn_usercart.__enter__.return_value = mock_conn_usercart
    mock_cursor_usercart = mock.MagicMock()
    mock_conn_usercart.cursor.return_value.__enter__.return_value = mock_cursor_usercart

    # fetchone() für:
    #   - SELECT user_carts => None (Cart existiert noch nicht)
    #   - SELECT seat_id FROM guest_cart_items => None (kein Konflikt)
    #   - INSERT => returning seat_id (777)
    #
    # Später ruft get_user_cart() evtl. fetchone() + fetchall() noch mal auf,
    # nach dem Capture. Da wir den Cart aber leeren, fetchall() => [].
    #
    mock_cursor_usercart.fetchone.side_effect = [
        None,      # user_carts => None
        None,      # guest_cart_items => None
        (777,),    # user_cart_items => seat_id=777
        # Falls dein Code später noch mal user_carts abfragt => erwarte dict
        {
            "user_id": 999,
            "valid_until": datetime.now(timezone.utc) + timedelta(minutes=15)
        },
        # Dann fetchall => []
    ]
    # fetchall => 2. Phase (nach dem Capture) => leerer Warenkorb:
    mock_cursor_usercart.fetchall.return_value = []

    mock_db_usercart.return_value = mock_conn_usercart

    # ----------------------------------------------------------------------------------
    # (B) DB/Mock-Setup für PayPal (capture => wir legen booking an)
    # ----------------------------------------------------------------------------------
    mock_conn_paypal = mock.MagicMock()
    mock_conn_paypal.__enter__.return_value = mock_conn_paypal
    mock_cursor_paypal = mock.MagicMock()
    mock_conn_paypal.cursor.return_value.__enter__.return_value = mock_cursor_paypal

    # Wenn wir capturing machen, führst du in `capture_paypal_order` typically aus:
    #   INSERT INTO bookings(...) RETURNING booking_id
    # => fetchone() => [1234]
    #
    mock_cursor_paypal.fetchone.side_effect = [
        [1234],   # booking_id=1234
    ]

    mock_db_paypal.return_value = mock_conn_paypal

    # Token-Decorator: um Auth abzufangen
    def token_required_decorator(f):
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapper
    mock_token_required.side_effect = token_required_decorator

    client = app.test_client()

    # ----------------------------------------------------------------------------------
    # Schritt 1: Sitz in User-Warenkorb hinzufügen
    # ----------------------------------------------------------------------------------
    add_payload = {
        "seat_id": 777,
        "price": 15.0,
        "showtime_id": 55,
        "seat_type_discount_id": None
    }
    resp_add = client.post(
        "/user/cart",
        json=add_payload,
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert resp_add.status_code == 201

    # ----------------------------------------------------------------------------------
    # Schritt 2: PayPal-Order erstellen
    # ----------------------------------------------------------------------------------
    mock_requests_post.return_value.status_code = 201
    mock_requests_post.return_value.json.return_value = {"id": "test_order_id_123"}

    create_order_resp = client.post("/paypal/create-order", json={"total_amount": "15"})
    assert create_order_resp.status_code == 200
    assert create_order_resp.get_json().get("orderID") == "test_order_id_123"

    # ----------------------------------------------------------------------------------
    # Schritt 3: PayPal-Order capturen => "COMPLETED"
    # ----------------------------------------------------------------------------------
    mock_requests_post.return_value.status_code = 201
    mock_requests_post.return_value.json.return_value = {"status": "COMPLETED"}

    capture_payload = {
        "orderID": "test_order_id_123",
        "vorname": "Hans",
        "nachname": "Meier",
        "email": "hans.meier@example.com",
        "total_amount": "15",  # <-- Als String, aber ganzzahlig
        "cart_items": [
            {
                "seat_id": 777,
                "showtime_id": 55,
                "seat_type_discount_id": None
            }
        ]
    }
    capture_resp = client.post("/paypal/capture-order", json=capture_payload, headers={"Authorization": f"Bearer {user_token}"})
    assert capture_resp.status_code == 200
    capture_data = capture_resp.get_json()
    assert capture_data.get("booking_id") == 1234, "Booking-ID sollte von DB-Mock zurückkommen"

    # ----------------------------------------------------------------------------------
    # Schritt 4: Prüfen, ob Warenkorb leer ist
    # ----------------------------------------------------------------------------------
    # Da du in capture_paypal_order() den user_cart leerst, sollte GET /user/cart => []
    #
    # fetchall() haben wir oben = [], also erhoffen wir uns hier .status_code = 200
    # und cart_items = []
    cart_resp = client.get("/user/cart", headers={"Authorization": f"Bearer {user_token}"})
    assert cart_resp.status_code == 200
    cart_data = cart_resp.get_json()
    assert cart_data.get("cart_items") == [], "Warenkorb sollte nach erfolgreicher Zahlung leer sein"
