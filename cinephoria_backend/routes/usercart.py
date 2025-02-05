
# cinephoria_backend/routes/usercart.py
from flask import Blueprint, jsonify, request
from cinephoria_backend.config import get_db_connection
from cinephoria_backend.routes.auth import token_required
import psycopg2.extras
from datetime import datetime, timedelta, timezone

user_cart_bp = Blueprint('user_cart', __name__)


def clear_expired_user_cart_items():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            delete_sql = """
                        WITH expired_users AS (
                            SELECT user_id
                            FROM user_carts
                            WHERE valid_until < NOW()
                        )

                        DELETE FROM user_carts
                        WHERE user_id IN (SELECT user_id FROM expired_users);
                    """
            cursor.execute(delete_sql)
            conn.commit()

@user_cart_bp.route('/user/cart', methods=['GET'])
@token_required
def get_user_cart():
    clear_expired_user_cart_items()
    user_id = request.user.get('user_id')
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # Überprüfen, ob der Benutzer einen Warenkorb hat und valid_until abrufen
                cursor.execute("SELECT user_id, valid_until FROM user_carts WHERE user_id = %s", (user_id,))
                cart = cursor.fetchone()
                if cart is None:
                    valid_until = datetime.now(timezone.utc) + timedelta(minutes=15)
                    cursor.execute("INSERT INTO user_carts (user_id, valid_until) VALUES (%s, %s)", (user_id, valid_until,))
                    conn.commit()
                    cart = {'user_id': user_id, 'valid_until': valid_until}
                else:
                    if cart['valid_until'] is None:
                        valid_until = datetime.now(timezone.utc) + timedelta(minutes=15)
                        cursor.execute("UPDATE user_carts SET valid_until = %s WHERE user_id = %s", (valid_until, user_id))
                        conn.commit()
                        cart['valid_until'] = valid_until

                # Abrufen der Warenkorb-Elemente mit showtime_id
                cursor.execute("""
                    SELECT seat_id, price, reserved_until, showtime_id, seat_type_discount_id
                    FROM user_cart_items
                    WHERE user_id = %s
                """, (user_id,))
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
        print(f"Fehler beim Abrufen des Warenkorbs: {e}")
        return jsonify({'error': 'Fehler beim Abrufen des Warenkorbs'}), 500





@user_cart_bp.route('/user/cart/<int:showtime_id>/<int:seat_id>', methods=['DELETE'])
@token_required
def remove_from_user_cart(showtime_id, seat_id):
    clear_expired_user_cart_items()
    user_id = request.user.get('user_id')
    
    if not showtime_id:
        return jsonify({'error': 'showtime_id ist erforderlich'}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                valid_until = datetime.now(timezone.utc) + timedelta(minutes=15)

                cursor.execute("""
                    UPDATE user_carts SET valid_until = %s WHERE user_id = %s
                """, (valid_until, user_id))
                # Entfernen des Sitzplatzes mit showtime_id
                cursor.execute("""
                    DELETE FROM user_cart_items
                    WHERE user_id = %s AND seat_id = %s AND showtime_id = %s
                """, (user_id, seat_id, showtime_id))
                conn.commit()
        return jsonify({'message': 'Sitzplatz aus dem Warenkorb entfernt'}), 200
    except Exception as e:
        print(f"Fehler beim Entfernen aus dem Warenkorb: {e}")
        return jsonify({'error': 'Fehler beim Entfernen aus dem Warenkorb'}), 500


@user_cart_bp.route('/user/cart', methods=['DELETE'])
@token_required
def clear_user_cart():
    user_id = request.user.get('user_id')
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                valid_until = datetime.now(timezone.utc) + timedelta(minutes=15)
                cursor.execute("""
                    UPDATE user_carts SET valid_until = %s WHERE user_id = %s
                               """, (valid_until, user_id))
                # Löschen aller Sitzplätze im Warenkorb
                cursor.execute("""
                    DELETE FROM user_cart_items
                    WHERE user_id = %s
                """, (user_id,))
                conn.commit()
        return jsonify({'message': 'Warenkorb geleert'}), 200
    except Exception as e:
        print(f"Fehler beim Leeren des Warenkorbs: {e}")
        return jsonify({'error': 'Fehler beim Leeren des Warenkorbs'}), 500
    



@user_cart_bp.route('/user/cart', methods=['POST'])
@token_required
def add_to_user_cart():
    clear_expired_user_cart_items()
    user_id = request.user.get('user_id')
    data = request.get_json()
    seat_id = data.get('seat_id')
    price = data.get('price')
    showtime_id = data.get('showtime_id')
    seat_type_discount_id = data.get('seat_type_discount_id')

    if not user_id or not seat_id or price is None or not showtime_id:
        return jsonify({'error': 'seat_id, price und showtime_id sind erforderlich'}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Sicherstellen, dass der Warenkorb existiert
                valid_until = datetime.now(timezone.utc) + timedelta(minutes=15)
                cursor.execute("SELECT user_id FROM user_carts WHERE user_id = %s", (user_id,))
                if cursor.fetchone() is None:
                    cursor.execute("INSERT INTO user_carts (user_id, valid_until) VALUES (%s, %s)", (user_id, valid_until,))
                    conn.commit()

                # Überprüfen, ob der Sitz bereits in guest_cart_items reserviert ist
                cursor.execute("""
                    SELECT seat_id FROM guest_cart_items 
                    WHERE seat_id = %s AND showtime_id = %s
                """, (seat_id, showtime_id))
                if cursor.fetchone():
                    return jsonify({'error': 'Der Sitzplatz ist bereits reserviert'}), 409

                # Reserviere den Sitzplatz
                reserved_until = datetime.now(timezone.utc) + timedelta(minutes=15)

                # Versuch, den Sitzplatz hinzuzufügen
                cursor.execute("""
                    INSERT INTO user_cart_items (user_id, seat_id, price, reserved_until, showtime_id, seat_type_discount_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (seat_id, showtime_id) DO NOTHING
                    RETURNING seat_id
                """, (user_id, seat_id, price, reserved_until, showtime_id, seat_type_discount_id))

                result = cursor.fetchone()

                if result is None:
                    # Der Sitzplatz ist bereits reserviert
                    return jsonify({'error': 'Der Sitzplatz ist bereits reserviert'}), 409

                # Aktualisieren Sie das gültige Ablaufdatum des Warenkorbs
                cursor.execute("""
                    UPDATE user_carts SET valid_until = %s WHERE user_id = %s
                """, (valid_until, user_id))
                conn.commit()

        return jsonify({'message': 'Sitzplatz zum Warenkorb hinzugefügt', 'reserved_until': reserved_until.isoformat()}), 201

    except Exception as e:
        print(f"Fehler beim Hinzufügen zum Warenkorb: {e}")
        return jsonify({'error': 'Fehler beim Hinzufügen zum Warenkorb'}), 500

#-->Um den Sitzen im Warenkorb einen Discount (ermäßigung) zu geben
@user_cart_bp.route('/user/cart/update', methods=['POST'])
@token_required
def update_user_cart():
    data = request.get_json()
    user_id = request.user.get('user_id')
    seat_id = data.get('seat_id')
    showtime_id = data.get('showtime_id')
    seat_type_discount_id = data.get('seat_type_discount_id')  # Kann null/None sein, um Rabatt zu entfernen

    # Grundlegende Validierung
    if not user_id or not seat_id or not showtime_id:
        return jsonify({'error': 'user_id, seat_id und showtime_id sind erforderlich'}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Überprüfen, ob der Sitz im Warenkorb des Benutzers existiert
                cursor.execute("""
                    SELECT cart_item_id, seat_type_discount_id
                    FROM user_cart_items
                    WHERE user_id = %s AND seat_id = %s AND showtime_id = %s
                """, (user_id, seat_id, showtime_id))
                cart_item = cursor.fetchone()

                if not cart_item:
                    return jsonify({'error': 'Der Sitzplatz ist nicht im Warenkorb des Benutzers'}), 404

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
                    UPDATE user_cart_items
                    SET seat_type_discount_id = %s
                    WHERE cart_item_id = %s
                """, (seat_type_discount_id, cart_item_id))

                conn.commit()

        return jsonify({'message': 'Warenkorb erfolgreich aktualisiert'}), 200

    except Exception as e:
        print(f"Fehler beim Aktualisieren des Warenkorbs: {e}")
        return jsonify({'error': 'Fehler beim Aktualisieren des Warenkorbs'}), 500