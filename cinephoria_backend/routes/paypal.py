# cinephoria_backend/routes/paypal.py
import jwt 
from flask import Blueprint, request, jsonify
import requests
import uuid
from cinephoria_backend.config import (
    PAYPAL_API_BASE,
    PAYPAL_CLIENT_ID,
    PAYPAL_CLIENT_SECRET,
    get_db_connection
)
from cinephoria_backend.routes.auth import token_optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

paypal_bp = Blueprint('paypal', __name__)

def get_paypal_access_token():
    response = requests.post(
        f"{PAYPAL_API_BASE}/v1/oauth2/token",
        headers={
            "Accept": "application/json",
            "Accept-Language": "en_US",
        },
        data={"grant_type": "client_credentials"},
        auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
    )
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(response.json())
        raise Exception('Failed to obtain PayPal access token')

@paypal_bp.route('/paypal/create-order', methods=['POST'])
def create_paypal_order():
    data = request.get_json()
    total_amount = data.get('total_amount')

    if not total_amount:
        return jsonify({"error": "total_amount ist erforderlich"}), 400

    try:
        access_token = get_paypal_access_token()
        url = f"{PAYPAL_API_BASE}/v2/checkout/orders"
        
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": "EUR",
                        "value": str(total_amount)
                    }
                }
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 201:
            print("Fehler beim Erstellen der PayPal-Order:", response.text)
            return jsonify({"error": "Failed to create PayPal order"}), 400

        order_data = response.json()
        order_id = order_data["id"]

        return jsonify({"orderID": order_id}), 200

    except Exception as e:
        print("Fehler in create_paypal_order:", e)
        return jsonify({"error": str(e)}), 500

@paypal_bp.route('/paypal/capture-order', methods=['POST'])
@token_optional
def capture_paypal_order():
    data = request.get_json()
    order_id = data.get('orderID')
    vorname = data.get('vorname')
    nachname = data.get('nachname')
    email = data.get('email')
    user_id = request.user.get('user_id') if request.user else None
    total_amount = data.get('total_amount')
    cart_items = data.get('cart_items', [])

    if not order_id or not vorname or not nachname or not email or total_amount is None or not cart_items:
        return jsonify({"error": "Fehlende Buchungsdaten"}), 400

    try:
        access_token = get_paypal_access_token()
        url = f"{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        response = requests.post(url, headers=headers)
        if response.status_code != 201:
            print("Fehler beim Capturen der PayPal-Order:", response.text)
            return jsonify({"error": "Failed to capture PayPal order"}), 400

        capture_data = response.json()

        if capture_data.get("status") == "COMPLETED":
            # Erzeuge QR-Code Tokens oder ähnliches
            qr_token = str(uuid.uuid4())
            qr_seite = str(uuid.uuid4())

            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Buchung in die bookings-Tabelle eintragen
                    cursor.execute("""
                        INSERT INTO bookings (
                            user_id,
                            booking_time,
                            payment_status,
                            total_amount,
                            paypal_order_id,
                            vorname,
                            nachname,
                            email,
                            qr_token,
                            qr_seite
                        )
                        VALUES (%s, CURRENT_TIMESTAMP, 'completed', %s, %s, %s, %s, %s, %s, %s)
                        RETURNING booking_id
                    """, (
                        user_id, 
                        total_amount,
                        order_id,
                        vorname,
                        nachname,
                        email,
                        qr_token,
                        qr_seite
                    ))
                    booking_id = cursor.fetchone()[0]

                    # Alle zugehörigen Sitzplätze (cart_items) in booking_seats eintragen
                    for item in cart_items:
                        seat_id = item.get('seat_id')
                        showtime_id = item.get('showtime_id')
                        seat_type_discount_id = item.get('seat_type_discount_id')
                        if not seat_id or not showtime_id:
                            conn.rollback()
                            return jsonify({"error": "Jedes cart_item braucht seat_id und showtime_id"}), 400

                        cursor.execute("""
                            INSERT INTO booking_seats 
                                (booking_id, seat_id, showtime_id, seat_type_discount_id)
                            VALUES (%s, %s, %s, %s)
                        """, (booking_id, seat_id, showtime_id, seat_type_discount_id))
                    
                    # --- Punkte gutschreiben ---
                    # Hier gehen wir davon aus, dass der total_amount korrekt übergeben wird.
                    # Falls du auf Nummer sicher gehen möchtest, kannst du alternativ auch
                    # nochmal über die cart_items anhand der DB-Preise den Gesamtbetrag berechnen.
                    if user_id is not None:
                        points_to_add = int(total_amount)  # 1 Euro = 1 Punkt

                        # Update der user_points-Tabelle
                        cursor.execute("""
                            UPDATE user_points
                            SET points = points + %s,
                                last_updated = CURRENT_TIMESTAMP
                            WHERE user_id = %s
                        """, (points_to_add, user_id))

                        # Protokollierung der Punkte-Transaktion
                        cursor.execute("""
                            INSERT INTO points_transactions (user_id, points_change, description)
                            VALUES (%s, %s, %s)
                        """, (user_id, points_to_add, f'Punkte für Buchung {booking_id}'))
                    else:
                        logging.error(f"USER_ID IST NULL: {user_id}")


                    conn.commit()

            return jsonify({
                "message": "Payment captured and booking completed",
                "booking_id": booking_id,
                "qr_token": qr_seite
            }), 200
        else:
            return jsonify({"error": "Payment was not completed"}), 400

    except Exception as e:
        print("Fehler in capture_paypal_order:", e)
        return jsonify({"error": str(e)}), 500
