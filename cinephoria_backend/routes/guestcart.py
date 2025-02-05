# cinephoria_backend/routes/guestcart.py
from flask import Blueprint, jsonify, request
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta, timezone
from psycopg2.errors import IntegrityError
from cinephoria_backend.config import get_db_connection

guest_cart_bp = Blueprint('guest_cart', __name__)


def clear_expired_guest_cart_items():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            delete_sql = """
                        WITH expired_guests AS (
                            SELECT guest_id
                            FROM guest_carts
                            WHERE valid_until < NOW()
                        )

                        DELETE FROM guest_carts
                        WHERE guest_id IN (SELECT guest_id FROM expired_guests);
                    """
            cursor.execute(delete_sql)
            conn.commit()




@guest_cart_bp.route('/guest/cart', methods=['GET'])
def get_guest_cart():
    clear_expired_guest_cart_items()  # Erst abgelaufene Einträge bereinigen
    guest_id = request.args.get('guest_id', None)
    if not guest_id:
        return jsonify({'error': 'guest_id ist erforderlich'}), 400
    
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # Prüfen ob guest_cart existiert und valid_until abrufen
                cursor.execute("SELECT guest_id, valid_until FROM guest_carts WHERE guest_id = %s", (guest_id,))
                cart = cursor.fetchone()
                if cart is None:
                    valid_until = datetime.now(timezone.utc) + timedelta(minutes=15)
                    cursor.execute(
                        "INSERT INTO guest_carts (guest_id, valid_until) VALUES (%s, %s)",
                        (guest_id, valid_until,)
                    )
                    conn.commit()
                    cart = {'guest_id': guest_id, 'valid_until': valid_until}
                else:
                    if cart['valid_until'] is None:
                        valid_until = datetime.now(timezone.utc) + timedelta(minutes=15)
                        cursor.execute("UPDATE guest_carts SET valid_until = %s WHERE guest_id = %s", (valid_until, guest_id))
                        conn.commit()
                        cart['valid_until'] = valid_until

                # Items abrufen
                cursor.execute("""
                    SELECT seat_id, price, reserved_until, showtime_id, seat_type_discount_id
                    FROM guest_cart_items
                    WHERE guest_id = %s
                """, (guest_id,))
                items = cursor.fetchall()
                cart_items = []
                for item in items:
                    cart_items.append({
                        'seat_id': item['seat_id'],
                        'price': float(item['price']),
                        'reserved_until': item['reserved_until'].isoformat(),
                        'showtime_id': item['showtime_id'],
                        'seat_type_discount_id': item['seat_type_discount_id']
                    })
        return jsonify({
            'valid_until': cart['valid_until'].astimezone(timezone.utc).isoformat() if cart['valid_until'] else None,
            'cart_items': cart_items
        }), 200
    except Exception as e:
        print(f"Fehler beim Abrufen des Guest-Warenkorbs: {e}")
        return jsonify({'error': 'Fehler beim Abrufen des Guest-Warenkorbs'}), 500


@guest_cart_bp.route('/guest/cart', methods=['POST'])
def add_to_guest_cart():
    clear_expired_guest_cart_items()  
    data = request.get_json()
    guest_id = data.get('guest_id')
    seat_id = data.get('seat_id')
    price = data.get('price')
    showtime_id = data.get('showtime_id')
    seat_type_discount_id = data.get('seat_type_discount_id')

    if not guest_id or not seat_id or price is None or not showtime_id:
        return jsonify({'error': 'guest_id, seat_id und price sind erforderlich und showtime_id'}), 400
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                valid_until = datetime.now(timezone.utc) + timedelta(minutes=15)
                
                # Sicherstellen, dass guest_carts existiert
                cursor.execute("SELECT guest_id FROM guest_carts WHERE guest_id = %s", (guest_id,))
                if cursor.fetchone() is None:
                    cursor.execute(
                        "INSERT INTO guest_carts (guest_id, valid_until) VALUES (%s, %s)",
                        (guest_id, valid_until,)
                    )

                # Überprüfen, ob der Sitz bereits in user_cart_items reserviert ist
                cursor.execute("""
                    SELECT seat_id FROM user_cart_items 
                    WHERE seat_id = %s AND showtime_id = %s
                """, (seat_id, showtime_id))
                if cursor.fetchone():
                    return jsonify({'error': 'Der Sitzplatz ist bereits reserviert'}), 409

                # Reserviere den Sitzplatz
                reserved_until = datetime.now(timezone.utc) + timedelta(minutes=15)

                # Versuch, den Sitzplatz hinzuzufügen
                cursor.execute("""
                    INSERT INTO guest_cart_items (guest_id, seat_id, price, reserved_until, showtime_id, seat_type_discount_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (seat_id, showtime_id) DO NOTHING
                    RETURNING seat_id
                """, (guest_id, seat_id, price, reserved_until, showtime_id, seat_type_discount_id))

                result = cursor.fetchone()

                if result is None:
                    # Der Sitzplatz ist bereits reserviert (falls using DO NOTHING RETURNING)
                    return jsonify({'error': 'Der Sitzplatz ist bereits reserviert'}), 409

                # Aktualisieren Sie das gültige Ablaufdatum des Warenkorbs
                cursor.execute("""
                    UPDATE guest_carts SET valid_until = %s WHERE guest_id = %s
                """, (valid_until, guest_id))
                conn.commit()

        return jsonify({'message': 'Sitzplatz zum Guest-Warenkorb hinzugefügt', 'reserved_until': reserved_until.isoformat()}), 201

    except IntegrityError as ie:
        # Spezifisches Abfangen von IntegrityError, falls nicht bereits behandelt
        return jsonify({'error': 'Der Sitzplatz ist bereits reserviert'}), 409
    except Exception as e:
        return jsonify({'error': 'Fehler beim Hinzufügen zum Guest-Warenkorb'}), 500

    

@guest_cart_bp.route('/guest/cart/<int:showtime_id>/<int:seat_id>', methods=['DELETE'])
def remove_from_guest_cart(showtime_id, seat_id):
    clear_expired_guest_cart_items()
    guest_id = request.args.get('guest_id', None)

    if not guest_id or not showtime_id:
        return jsonify({'error': 'guest_id und showtime_id sind erforderlich'}), 400
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                valid_until = datetime.now(timezone.utc) + timedelta(minutes=15)
                cursor.execute("""
                    UPDATE guest_carts SET valid_until = %s WHERE guest_id = %s
                """, (valid_until, guest_id))
                # Entfernen des Sitzplatzes mit showtime_id
                cursor.execute("""
                    DELETE FROM guest_cart_items
                    WHERE guest_id = %s AND seat_id = %s AND showtime_id = %s
                """, (guest_id, seat_id, showtime_id))
                conn.commit()
        return jsonify({'message': 'Sitzplatz aus dem Guest-Warenkorb entfernt'}), 200
    except Exception as e:
        print(f"Fehler beim Entfernen aus dem Guest-Warenkorb: {e}")
        return jsonify({'error': 'Fehler beim Entfernen aus dem Guest-Warenkorb'}), 500


@guest_cart_bp.route('/guest/cart', methods=['DELETE'])
def clear_guest_cart():
    clear_expired_guest_cart_items()
    guest_id = request.args.get('guest_id', None)
    if not guest_id:
        return jsonify({'error': 'guest_id ist erforderlich'}), 400
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                valid_until = datetime.now(timezone.utc) + timedelta(minutes=15)
                cursor.execute("""
                    UPDATE guest_carts SET valid_until = %s WHERE guest_id = %s
                               """, (valid_until, guest_id))
                # Löschen aller Sitzplätze im Guest-Warenkorb
                cursor.execute("""
                    DELETE FROM guest_cart_items
                    WHERE guest_id = %s
                """, (guest_id,))
                conn.commit()
        return jsonify({'message': 'Guest-Warenkorb geleert'}), 200
    except Exception as e:
        print(f"Fehler beim Leeren des Guest-Warenkorbs: {e}")
        return jsonify({'error': 'Fehler beim Leeren des Guest-Warenkorbs'}), 500
    


@guest_cart_bp.route('/guest/cart/update', methods=['POST'])
def update_guest_cart():
    data = request.get_json()
    guest_id = data.get('guest_id')  # Stelle sicher, dass guest_id übermittelt wird
    seat_id = data.get('seat_id')
    showtime_id = data.get('showtime_id')
    seat_type_discount_id = data.get('seat_type_discount_id')  # Kann null/None sein, um Rabatt zu entfernen

    # Grundlegende Validierung
    if not guest_id or not seat_id or not showtime_id:
        return jsonify({'error': 'guest_id, seat_id und showtime_id sind erforderlich'}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Überprüfen, ob der Sitz im Warenkorb des Gastes existiert
                cursor.execute("""
                    SELECT cart_item_id, seat_type_discount_id
                    FROM guest_cart_items
                    WHERE guest_id = %s AND seat_id = %s AND showtime_id = %s
                """, (guest_id, seat_id, showtime_id))
                cart_item = cursor.fetchone()

                if not cart_item:
                    return jsonify({'error': 'Der Sitzplatz ist nicht im Gast-Warenkorb'}), 404

                cart_item_id, current_discount_id = cart_item

                if seat_type_discount_id:
                    # Validierung des seat_type_discount_id
                    cursor.execute("""
                        SELECT 1 
                        FROM seat_type_discounts 
                        WHERE seat_type_discount_id = %s 
                        AND seat_type_id = (
                            SELECT seat_type_id FROM seats WHERE seat_id = %s
                        )
                    """, (seat_type_discount_id, seat_id))
                    if not cursor.fetchone():
                        return jsonify({'error': 'Ungültiger seat_type_discount_id für den angegebenen Sitzplatz'}), 400

                # Aktualisieren des seat_type_discount_id (kann auch NULL sein)
                cursor.execute("""
                    UPDATE guest_cart_items
                    SET seat_type_discount_id = %s
                    WHERE cart_item_id = %s
                """, (seat_type_discount_id, cart_item_id))

                conn.commit()

        return jsonify({'message': 'Gast-Warenkorb erfolgreich aktualisiert'}), 200

    except Exception as e:
        print(f"Fehler beim Aktualisieren des Gast-Warenkorbs: {e}")
        return jsonify({'error': 'Fehler beim Aktualisieren des Gast-Warenkorbs'}), 500