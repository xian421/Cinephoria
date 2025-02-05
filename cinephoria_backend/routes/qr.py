# cinephoria_backend QR-Code-Endpunkte

from flask import Blueprint, jsonify, request
from psycopg2.extras import RealDictCursor
from cinephoria_backend.config import get_db_connection

qr_bp = Blueprint('qr', __name__)



#Hier QR-Code
@qr_bp.route('/read/qrcode/<token>', methods=['GET'])
def read_qrcode(token):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Zuerst die Buchung anhand des QR-Tokens abrufen
                cursor.execute("""
                    SELECT booking_id, user_id, booking_time, payment_status, total_amount, 
                           created_at, paypal_order_id, email, nachname, vorname, qr_token
                    FROM bookings
                    WHERE qr_seite = %s
                """, (token,))
                booking = cursor.fetchone()

                if not booking:
                    return jsonify({"error": "Buchung nicht gefunden"}), 404

                booking_id = booking['booking_id']

                # Verwende das erweiterte SQL-Statement, um detaillierte Buchungsinformationen zu erhalten
                cursor.execute("""
                    SELECT 
                        s.number AS nummer,
                        s.row AS reihe,
                        st.name AS type,
                        st.color AS farbe,
                        st.icon AS type_icon,
                        std.discount_percentage,
                        std.discount_amount,
                        d.name AS discount,
                        d.description AS discount_infos,
                        sh.movie_id,
                        sh.start_time,
                        sh.end_time,
                        sc.name AS kinosaal
                    FROM booking_seats bs
                    JOIN seats s ON s.seat_id = bs.seat_id
                    JOIN seat_types st ON st.seat_type_id = s.seat_type_id
                    LEFT JOIN seat_type_discounts std ON std.seat_type_discount_id = bs.seat_type_discount_id
                    LEFT JOIN discounts d ON d.discount_id = std.discount_id
                    JOIN showtimes sh ON sh.showtime_id = bs.showtime_id
                    JOIN screens sc ON sc.screen_id = sh.screen_id
                    WHERE bs.booking_id = %s
                """, (booking_id,))
                seats = cursor.fetchall()

                # Gruppiere die Sitzplätze nach movie_id
                movies = {}
                for seat in seats:
                    movie_id = seat['movie_id']
                    if movie_id not in movies:
                        movies[movie_id] = {
                            "movie_id": movie_id,
                            "start_time": seat['start_time'].isoformat(),
                            "end_time": seat['end_time'].isoformat(),
                            "kinosaal": seat['kinosaal'],
                            "seats": []
                        }
                    # Entferne redundante Felder aus dem Sitzplatz-Dictionary
                    seat_data = {
                        "nummer": seat['nummer'],
                        "reihe": seat['reihe'],
                        "type": seat['type'],
                        "farbe": seat['farbe'],
                        "type_icon": seat['type_icon'],
                        "discount_percentage": seat['discount_percentage'],
                        "discount_amount": seat['discount_amount'],
                        "discount_name": seat['discount'],
                        "discount_infos": seat['discount_infos']
                    }
                    movies[movie_id]["seats"].append(seat_data)

                # Strukturierte Buchungsdaten zusammenstellen
                booking_data = {
                    "booking_id": booking['booking_id'],
                    "user_id": booking['user_id'],
                    "booking_time": booking['booking_time'].isoformat(),
                    "payment_status": booking['payment_status'],
                    "total_amount": float(booking['total_amount']),
                    "created_at": booking['created_at'].isoformat(),
                    "paypal_order_id": booking['paypal_order_id'],
                    "email": booking['email'],
                    "nachname": booking['nachname'],
                    "vorname": booking['vorname'],
                    "qr_token": booking['qr_token'],
                    "movies": list(movies.values())  # Liste der Filme mit zugehörigen Sitzplätzen
                }

        return jsonify(booking_data), 200

    except Exception as e:
        return jsonify({"error": "Interner Serverfehler"}), 500


@qr_bp.route('/mitarbeiter/read/qrcode/<token>', methods=['GET'])
def read_qrcode_mitarbeiter(token):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Abrufen der Buchung basierend auf dem QR-Token
                cursor.execute("""
                    SELECT booking_id, user_id, booking_time, payment_status, total_amount, 
                           created_at, paypal_order_id, email, nachname, vorname, qr_token
                    FROM bookings
                    WHERE qr_token = %s
                """, (token,))
                booking = cursor.fetchone()

                if not booking:
                    return jsonify({"error": "Buchung nicht gefunden"}), 404

                booking_id = booking['booking_id']

                # Abrufen der Sitzplatzinformationen
                cursor.execute("""
                    SELECT 
                        s.number AS nummer,
                        s.row AS reihe,
                        st.name AS type,
                        st.color AS farbe,
                        st.icon AS type_icon,
                        std.discount_percentage,
                        std.discount_amount,
                        d.name AS discount,
                        d.description AS discount_infos,
                        sh.movie_id,
                        sh.start_time,
                        sh.end_time,
                        sc.name AS kinosaal
                    FROM booking_seats bs
                    JOIN seats s ON s.seat_id = bs.seat_id
                    JOIN seat_types st ON st.seat_type_id = s.seat_type_id
                    LEFT JOIN seat_type_discounts std ON std.seat_type_discount_id = bs.seat_type_discount_id
                    LEFT JOIN discounts d ON d.discount_id = std.discount_id
                    JOIN showtimes sh ON sh.showtime_id = bs.showtime_id
                    JOIN screens sc ON sc.screen_id = sh.screen_id
                    WHERE bs.booking_id = %s
                """, (booking_id,))
                seats = cursor.fetchall()

                # Gruppiere die Sitzplätze nach movie_id
                movies = {}
                for seat in seats:
                    movie_id = seat['movie_id']
                    if movie_id not in movies:
                        movies[movie_id] = {
                            "movie_id": movie_id,
                            "start_time": seat['start_time'].isoformat(),
                            "end_time": seat['end_time'].isoformat(),
                            "kinosaal": seat['kinosaal'],
                            "seats": []
                        }
                    # Sitzplatzdaten
                    seat_data = {
                        "nummer": seat['nummer'],
                        "reihe": seat['reihe'],
                        "type": seat['type'],
                        "farbe": seat['farbe'],
                        "type_icon": seat['type_icon'],
                        "discount_name": seat['discount'],
                        "discount_infos": seat['discount_infos']
                    }
                    movies[movie_id]["seats"].append(seat_data)

                # Strukturierte Buchungsdaten
                booking_data = {
                    "booking_id": booking['booking_id'],
                    "user_id": booking['user_id'],
                    "booking_time": booking['booking_time'].isoformat(),
                    "payment_status": booking['payment_status'],
                    "total_amount": float(booking['total_amount']),
                    "created_at": booking['created_at'].isoformat(),
                    "paypal_order_id": booking['paypal_order_id'],
                    "email": booking['email'],
                    "nachname": booking['nachname'],
                    "vorname": booking['vorname'],
                    "qr_token": booking['qr_token'],
                    "movies": list(movies.values())  # Liste der Filme mit zugehörigen Sitzplätzen
                }

        return jsonify(booking_data), 200

    except Exception as e:
        return jsonify({"error": "Interner Serverfehler"}), 500

