# app.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import IntegrityError
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
import uuid
import logging
import subprocess

from cinephoria_backend.config import (
    DATABASE_URL,
    TMDB_API_URL,
    HEADERS,
    SECRET_KEY,
)
from cinephoria_backend.routes.movies import movies_bp
from cinephoria_backend.routes.auth import auth_bp, token_required, admin_required
from cinephoria_backend.routes.paypal import paypal_bp
from cinephoria_backend.routes.seats import seats_bp
from cinephoria_backend.routes.seat_types import seat_types_bp
from cinephoria_backend.routes.showtimes import showtimes_bp
from cinephoria_backend.routes.usercart import user_cart_bp
from cinephoria_backend.routes.guestcart import guest_cart_bp
# from cinephoria_backend.routes.cinemas import cinemas_bp
# from cinephoria_backend.routes.screens import screens_bp
# from cinephoria_backend.routes.bookings import bookings_bp
# from cinephoria_backend.routes.qr import qr_bp
# from cinephoria_backend.routes.supermarkt import supermarkt_bp
from cinephoria_backend.routes.discounts import discounts_bp
from cinephoria_backend.routes.extras import extras_bp  



app = Flask(__name__, static_folder='public', static_url_path='')


# Einzelne Module verwenden
app.register_blueprint(movies_bp, url_prefix='')
app.register_blueprint(auth_bp, url_prefix='')
app.register_blueprint(paypal_bp, url_prefix='')
app.register_blueprint(seats_bp, url_prefix='')
app.register_blueprint(seat_types_bp, url_prefix='')
app.register_blueprint(showtimes_bp, url_prefix='')
app.register_blueprint(user_cart_bp, url_prefix='')
app.register_blueprint(guest_cart_bp, url_prefix='')
# app.register_blueprint(cinemas_bp, url_prefix='')
# app.register_blueprint(screens_bp, url_prefix='')
# app.register_blueprint(bookings_bp, url_prefix='')
# app.register_blueprint(qr_bp, url_prefix='')
# app.register_blueprint(supermarkt_bp, url_prefix='')
app.register_blueprint(discounts_bp, url_prefix='')
app.register_blueprint(extras_bp, url_prefix='')




logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CORS(app, resources={
    r"/*": {
        "origins": [
            "https://cinephoria-theta.vercel.app",
            "http://localhost:5173"
        ],
        "methods": ["GET", "POST", "DELETE", "OPTIONS", "PUT"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})




#Hier QR-Code
@app.route('/read/qrcode/<token>', methods=['GET'])
def read_qrcode(token):
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
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
        logging.error(f"Fehler in read_qrcode: {e}")
        return jsonify({"error": "Interner Serverfehler"}), 500


@app.route('/cinemas', methods=['GET'])
def get_cinemas():
    try:
        with psycopg2.connect(DATABASE_URL) as conn:  
            with conn.cursor() as cursor:            
                cursor.execute("SELECT cinema_id, name, location, contact_number FROM cinema")
                result = cursor.fetchall()

                cinemas = [
                    {
                        'cinema_id': row[0],
                        'name': row[1],
                        'location': row[2],
                        'contact_number': row[3]
                    }
                    for row in result
                ]

        return jsonify({'cinemas': cinemas}), 200

    except Exception as e:
        print(f"Fehler: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der Kinos'}), 500

@app.route('/screens', methods=['GET'])
def get_screens():
    cinema_id = request.args.get('cinema_id', default=1, type=int)  # Standardwert: 1
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT s.screen_id, s.name, s.capacity, s.type, s.created_at, COALESCE(s.updated_at, s.created_at)
                    FROM screens s
                    JOIN cinema c ON c.cinema_id = s.cinema_id
                    WHERE c.cinema_id = %s
                """, (cinema_id,))
                
                result = cursor.fetchall()

                screens = [
                    {
                        'screen_id': row[0],
                        'name': row[1],
                        'capacity': row[2],
                        'type': row[3],
                        'created_at': row[4],
                        'updated_at': row[5]
                    }
                    for row in result
                ]

        return jsonify({'screens': screens}), 200

    except Exception as e:
        print(f"Fehler: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der Kinosäle'}), 500




# @app.route('/bookings', methods=['POST']) #Dashierändern
# @token_required
# def create_booking_route():
#     data = request.get_json()
#     showtime_id = data.get('showtime_id')
#     seat_ids = data.get('seat_ids')  # Liste von seat_id
#     user_id = request.user.get('user_id')  # Aus dem Token
#     order_id = data.get('order_id')  # Neue PayPal Order ID

#     if not showtime_id or not seat_ids or not order_id:
#         return jsonify({'error': 'showtime_id, seat_ids und order_id sind erforderlich'}), 400

#     try:
#         with psycopg2.connect(DATABASE_URL) as conn:
#             with conn.cursor() as cursor:
#                 # Beginne eine Transaktion
#                 cursor.execute("BEGIN;")
                
#                 # Ermitteln des Kinosaals für die Showtime
#                 cursor.execute("""
#                     SELECT screen_id FROM showtimes WHERE showtime_id = %s
#                 """, (showtime_id,))
#                 screen = cursor.fetchone()
#                 if not screen:
#                     conn.rollback()
#                     return jsonify({'error': 'Showtime nicht gefunden'}), 404
#                 screen_id = screen[0]
                
#                 # Überprüfen, ob die Sitzplätze zur Showtime gehören und verfügbar sind
#                 cursor.execute("""
#                     SELECT seat_id FROM seats
#                     WHERE seat_id = ANY(%s) AND screen_id = %s
#                 """, (seat_ids, screen_id))
#                 available_seats = {row[0] for row in cursor.fetchall()}
                
#                 if not available_seats.issuperset(set(seat_ids)):
#                     conn.rollback()
#                     return jsonify({'error': 'Ein oder mehrere Sitzplätze sind nicht verfügbar'}), 400
                
#                 # Überprüfen, ob die Sitzplätze bereits gebucht wurden
#                 cursor.execute("""
#                     SELECT bs.seat_id FROM booking_seats bs
#                     JOIN bookings b ON bs.booking_id = b.booking_id
#                     WHERE bs.showtime_id = %s AND b.payment_status = 'completed' AND bs.seat_id = ANY(%s)
#                     FOR UPDATE
#                 """, (showtime_id, seat_ids))
#                 already_booked = {row[0] for row in cursor.fetchall()}
                
#                 if already_booked:
#                     conn.rollback()
#                     return jsonify({'error': 'Ein oder mehrere Sitzplätze sind bereits gebucht'}), 400
                
#                 # Preise für die ausgewählten Sitzplätze abrufen
#                 cursor.execute("""
#                     SELECT s.seat_id, st.price
#                     FROM seats s
#                     JOIN seat_types st ON s.seat_type_id = st.seat_type_id
#                     WHERE s.seat_id = ANY(%s)
#                 """, (seat_ids,))
#                 seat_prices = cursor.fetchall()
#                 seat_price_dict = {seat_id: price for seat_id, price in seat_prices}
                
#                 # Gesamtbetrag berechnen
#                 total_amount = sum(seat_price_dict[seat_id] for seat_id in seat_ids)
                
#                 # Erstellen der Buchung
#                 cursor.execute("""
#                     INSERT INTO bookings (user_id, showtime_id, payment_status, total_amount, paypal_order_id)
#                     VALUES (%s, %s, %s, %s, %s)
#                     RETURNING booking_id
#                 """, (user_id, showtime_id, 'completed', total_amount, order_id))
#                 booking_id = cursor.fetchone()[0]
                
#                 # Verknüpfen der Sitzplätze mit der Buchung und deren Preis
#                 for seat_id in seat_ids:
#                     price = seat_price_dict[seat_id]
#                     cursor.execute("""
#                         INSERT INTO booking_seats (booking_id, seat_id, price)
#                         VALUES (%s, %s, %s)
#                     """, (booking_id, seat_id, price))
                
#                 # **Neuer Code: Punkte gutschreiben**
#                 points_to_add = int(total_amount)  # 1 Euro = 1 Punkt

#                 # Aktualisiere user_points
#                 cursor.execute("""
#                     UPDATE user_points
#                     SET points = points + %s,
#                         last_updated = CURRENT_TIMESTAMP
#                     WHERE user_id = %s
#                 """, (points_to_add, user_id))

#                 # Protokolliere die Punkte-Transaktion
#                 cursor.execute("""
#                     INSERT INTO points_transactions (user_id, points_change, description)
#                     VALUES (%s, %s, %s)
#                 """, (user_id, points_to_add, f'Punkte für Buchung {booking_id}'))

#                 # Commit der Transaktion
#                 conn.commit()
        
#         return jsonify({'message': 'Buchung erfolgreich', 'booking_id': booking_id}), 201
#     except Exception as e:
#         print(f"Fehler beim Erstellen der Buchung: {e}")
#         return jsonify({'error': 'Fehler beim Erstellen der Buchung'}), 500

    

@app.route('/bookings', methods=['GET'])
@token_required
def get_user_bookings():
    user_id = request.user.get('user_id')
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:

                cursor.execute("""
                    SELECT 
                        b.booking_id, 
                        bs.showtime_id, 
                        b.total_amount,
                        b.payment_status,
                        b.paypal_order_id,
                        b.created_at, 
                        s.movie_id, 
                        s.screen_id, 
                        s.start_time, 
                        s.end_time,
                        sc.name AS screen_name
                    FROM bookings b
                    JOIN booking_seats bs ON b.booking_id = bs.booking_id
                    JOIN showtimes s ON bs.showtime_id = s.showtime_id
                    JOIN screens sc ON s.screen_id = sc.screen_id
                    WHERE b.user_id = %s
                    ORDER BY b.created_at DESC
                """, (user_id,))
                bookings = cursor.fetchall()

                if not bookings:
                    return jsonify({'bookings': []}), 200

                # Sammeln aller eindeutigen movie_ids
                movie_ids = list({booking['movie_id'] for booking in bookings})

                # Abrufen der Buchungs-Sitzplätze
                booking_ids = [booking['booking_id'] for booking in bookings]
                cursor.execute("""
                    SELECT 
                        bs.booking_id, 
                        bs.seat_id, 
                        bs.price,
                        s.row,
                        s.number,
                        st.name AS seat_type,
                        bs.seat_type_discount_id      
                    FROM booking_seats bs
                    JOIN seats s ON bs.seat_id = s.seat_id
                    JOIN seat_types st ON s.seat_type_id = st.seat_type_id
                    WHERE bs.booking_id = ANY(%s)
                """, (booking_ids,))
                booking_seats = cursor.fetchall()

                # Mapping von booking_id zu Sitzplätzen
                seats_map = {}
                for bs in booking_seats:
                    booking_id = bs['booking_id']
                    seat = {
                        'seat_id': bs['seat_id'],
                        'price': float(bs['price']) if bs['price'] is not None else 0,
                        'row': bs['row'],
                        'number': bs['number'],
                        'seat_type': bs['seat_type'],
                        'seat_type_discount_id': bs['seat_type_discount_id']
                    }
                    seats_map.setdefault(booking_id, []).append(seat)

        # Abrufen der Filmdetails von TMDB für jede eindeutige movie_id
        movie_details = {}
        for movie_id in movie_ids:
            movie_response = requests.get(f"{TMDB_API_URL}/{movie_id}?language=de-DE", headers=HEADERS)
            if movie_response.status_code == 200:
                movie_data = movie_response.json()
                movie_details[movie_id] = {
                    'title': movie_data.get('title'),
                    'poster_url': f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path')}" if movie_data.get('poster_path') else None
                }
            else:
                movie_details[movie_id] = {
                    'title': None,
                    'poster_url': None
                }

        # Aufbau der finalen Buchungsstruktur
        bookings_list = []
        for booking in bookings:
            movie_id = booking['movie_id']
            movie_info = movie_details.get(movie_id, {})
            booking_dict = {
                'booking_id': booking['booking_id'],
                'showtime_id': booking['showtime_id'],
                'total_amount': float(booking['total_amount']) if booking['total_amount'] is not None else 0,
                'payment_status': booking['payment_status'],
                'paypal_order_id': booking['paypal_order_id'],
                'created_at': booking['created_at'].isoformat(),
                'movie_id': movie_id,
                'movie_title': movie_info.get('title'),
                'movie_poster_url': movie_info.get('poster_url'),
                'screen_id': booking['screen_id'],
                'start_time': booking['start_time'].isoformat(),
                'end_time': booking['end_time'].isoformat() if booking['end_time'] else None,
                'screen_name': booking['screen_name'],
                'seats': seats_map.get(booking['booking_id'], [])
            }
            bookings_list.append(booking_dict)

        return jsonify({'bookings': bookings_list}), 200

    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Buchungen: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der Buchungen'}), 500


    

# @app.route('/bookings/new', methods=['POST'])
# def create_booking():
#     data = request.get_json()
#     vorname = data.get('vorname')
#     nachname = data.get('nachname')
#     email = data.get('email')
#     user_id = data.get('user_id')  # Kann null/None sein
#     total_amount = data.get('total_amount')
#     paypal_order_id = data.get('paypal_order_id', 111)
#     cart_items = data.get('cart_items', [])
#     seat_type_discount = data.get('seat_type_discount')

#     # Grundlegende Validierung
#     if not vorname or not nachname or not email:
#         return jsonify({"error": "Vorname, Nachname und Email sind erforderlich"}), 400
#     if not cart_items:
#         return jsonify({"error": "cart_items darf nicht leer sein"}), 400
#     if total_amount is None:
#         return jsonify({"error": "total_amount ist erforderlich"}), 400

#     try:
#         with psycopg2.connect(DATABASE_URL) as conn:
#             with conn.cursor() as cursor:
#                 # Erstelle einen Buchungseintrag
#                 # payment_status immer 'completed'
#                 # booking_time mit CURRENT_TIMESTAMP
#                 # user_id kann NULL sein, daher verwenden wir bedingte Platzhalter
#                 cursor.execute("""
#                     INSERT INTO bookings (user_id, booking_time, payment_status, total_amount, paypal_order_id, vorname, nachname, email)
#                     VALUES (%s, CURRENT_TIMESTAMP, 'completed', %s, %s, %s, %s, %s)
#                     RETURNING booking_id
#                 """, (user_id, total_amount, paypal_order_id, vorname, nachname, email))
#                 booking_id = cursor.fetchone()[0]

#                 # Nun die booking_seats einfügen
#                 # Für jeden Eintrag in cart_items einen Insert
#                 # price lassen wir leer, also NULL
#                 for item in cart_items:
#                     seat_id = item.get('seat_id')
#                     showtime_id = item.get('showtime_id')
#                     seat_type_discount_id = item.get('seat_type_discount_id')  
#                     if not seat_id or not showtime_id:
#                         conn.rollback()
#                         return jsonify({"error": "Jedes cart_item braucht seat_id und showtime_id"}), 400

#                     # Füge den Sitz in booking_seats ein
#                     cursor.execute("""
#                         INSERT INTO booking_seats (booking_id, seat_id, showtime_id, seat_type_discount_id)
#                         VALUES (%s, %s, %s, %s)
#                     """, (booking_id, seat_id, showtime_id, seat_type_discount_id))

#                 conn.commit()

#         return jsonify({"message": "Buchung erfolgreich angelegt", "booking_id": booking_id}), 201
#     except Exception as e:
#         print(f"Fehler beim Erstellen der Buchung: {e}")
#         return jsonify({"error": "Fehler beim Erstellen der Buchung"}), 500



    




#############################################################################################################
###################################     Hier Supermarktkasse    #############################################
#############################################################################################################

@app.route('/supermarkt/items', methods=['GET'])
@admin_required
def get_supermarkt_items():
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        si.item_id, si.barcode, si.item_name, si.price, si.category, 
                        si.created_at, si.updated_at, 
                        sp.pfand_id, sp.amount, sp.name AS pfand_name, sp.description
                    FROM supermarkt_items si
                    LEFT JOIN supermarkt_pfand sp ON si.pfand_id = sp.pfand_id
                """)
                items = cursor.fetchall()
                items_list = [dict(i) for i in items]
        return jsonify({'items': items_list}), 200
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Supermarkt-Items: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der Supermarkt-Items'}), 500

@app.route('/supermarkt/items', methods=['POST'])
@admin_required
def add_supermarkt_item():
    data = request.get_json()
    barcode = data.get('barcode')
    item_name = data.get('item_name')
    price = data.get('price')
    category = data.get('category')
    pfand_id = data.get('pfand_id')  # Fremdschlüssel
    
    if not barcode or not item_name or not price or not category:
        return jsonify({'error': 'Barcode, Item Name, Preis und Kategorie sind erforderlich'}), 400

    if pfand_id is not None and not isinstance(pfand_id, int):
        return jsonify({'error': 'Pfand ID muss eine Ganzzahl sein'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                # Überprüfe, ob pfand_id existiert, falls angegeben
                if pfand_id:
                    cursor.execute("SELECT pfand_id FROM supermarkt_pfand WHERE pfand_id = %s", (pfand_id,))
                    if cursor.fetchone() is None:
                        return jsonify({'error': 'Ungültige Pfand ID'}), 400

                cursor.execute("""
                    INSERT INTO supermarkt_items (barcode, item_name, price, category, pfand_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING 
                        supermarkt_items.item_id, 
                        supermarkt_items.barcode, 
                        supermarkt_items.item_name, 
                        supermarkt_items.price, 
                        supermarkt_items.category, 
                        supermarkt_items.created_at, 
                        supermarkt_items.updated_at, 
                        supermarkt_items.pfand_id,
                        (SELECT name FROM supermarkt_pfand WHERE supermarkt_pfand.pfand_id = supermarkt_items.pfand_id) AS pfand_name
                """, (barcode, item_name, price, category, pfand_id))
                new_item = cursor.fetchone()
                columns = [desc[0] for desc in cursor.description]
                new_item_dict = dict(zip(columns, new_item))
                conn.commit()
                return jsonify({'item': new_item_dict}), 201
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({'error': 'Ein Artikel mit diesem Barcode existiert bereits'}), 400
    except Exception as e:
        logger.error(f"Fehler beim Hinzufügen des Supermarkt-Items: {e}")
        return jsonify({'error': 'Fehler beim Hinzufügen des Supermarkt-Items'}), 500

    

@app.route('/supermarkt/items/<int:item_id>', methods=['PUT'])
@admin_required
def update_supermarkt_item(item_id):
    data = request.get_json()
    barcode = data.get('barcode')
    item_name = data.get('item_name')
    price = data.get('price')
    category = data.get('category')
    pfand_id = data.get('pfand_id')  # Fremdschlüssel

    if not barcode or not item_name or not price or not category:
        return jsonify({'error': 'Barcode, Item Name, Preis und Kategorie sind erforderlich'}), 400

    if pfand_id is not None and not isinstance(pfand_id, int):
        return jsonify({'error': 'Pfand ID muss eine Ganzzahl sein'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                # Überprüfe, ob pfand_id existiert
                if pfand_id:
                    cursor.execute("SELECT pfand_id FROM supermarkt_pfand WHERE pfand_id = %s", (pfand_id,))
                    if cursor.fetchone() is None:
                        return jsonify({'error': 'Ungültige Pfand ID'}), 400

                cursor.execute("""
                    UPDATE supermarkt_items
                    SET barcode = %s,
                        item_name = %s,
                        price = %s,
                        category = %s,
                        pfand_id = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE item_id = %s
                    RETURNING 
                        supermarkt_items.item_id, 
                        supermarkt_items.barcode, 
                        supermarkt_items.item_name, 
                        supermarkt_items.price, 
                        supermarkt_items.category, 
                        supermarkt_items.created_at, 
                        supermarkt_items.updated_at, 
                        supermarkt_items.pfand_id,
                        (SELECT name FROM supermarkt_pfand WHERE supermarkt_pfand.pfand_id = supermarkt_items.pfand_id) AS pfand_name
                """, (barcode, item_name, price, category, pfand_id, item_id))
                updated_item = cursor.fetchone()
                if updated_item:
                    columns = [desc[0] for desc in cursor.description]
                    updated_item_dict = dict(zip(columns, updated_item))
                    conn.commit()
                    return jsonify({'item': updated_item_dict}), 200
                else:
                    return jsonify({'error': 'Item nicht gefunden'}), 404
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({'error': 'Ein Artikel mit diesem Barcode existiert bereits'}), 400
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren des Supermarkt-Items: {e}")
        return jsonify({'error': 'Fehler beim Aktualisieren des Supermarkt-Items'}), 500


@app.route('/supermarkt/items/<int:item_id>', methods=['DELETE'])
@admin_required
def delete_supermarkt_item(item_id):
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM supermarkt_items WHERE item_id = %s RETURNING item_id", (item_id,))
                deleted_item = cursor.fetchone()
                if deleted_item:
                    conn.commit()
                    return jsonify({'message': 'Artikel erfolgreich gelöscht'}), 200
                else:
                    return jsonify({'error': 'Artikel nicht gefunden'}), 404
    except Exception as e:
        logger.error(f"Fehler beim Löschen des Supermarkt-Items: {e}")
        return jsonify({'error': 'Fehler beim Löschen des Supermarkt-Items'}), 500



@app.route('/supermarkt/items/barcode/<string:barcode>', methods=['GET'])
def get_supermarkt_item_by_barcode(barcode):
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        si.item_id, si.barcode, si.item_name, si.price, si.category, 
                        si.created_at, si.updated_at, 
                        sp.pfand_id, sp.amount, sp.name AS pfand_name, sp.description
                    FROM supermarkt_items si
                    LEFT JOIN supermarkt_pfand sp ON si.pfand_id = sp.pfand_id
                    WHERE si.barcode = %s
                """, (barcode,))
                item = cursor.fetchone()
                if item:
                    item_dict = dict(item)
                    # Setze 'pfand_name' auf 'Kein Pfand', wenn 'pfand_id' NULL ist
                    if item_dict['pfand_id'] is None:
                        item_dict['pfand_name'] = 'Kein Pfand'
                        item_dict['amount'] = 0.0
                    else:
                        # Sicherstellen, dass 'amount' ein Float ist
                        item_dict['amount'] = float(item_dict['amount'])
                    
                    # Sicherstellen, dass 'price' ein Float ist
                    item_dict['price'] = float(item_dict['price'])
                    
                    logger.info(f"Found item: {item_dict}")
                    return jsonify(item_dict), 200
                else:
                    logger.info("Artikel nicht gefunden")
                    return jsonify({'error': 'Artikel nicht gefunden'}), 404
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Supermarkt-Items: {e}")
        return jsonify({'error': 'Fehler beim Abrufen des Supermarkt-Items'}), 500

                                   
# ###############Pfand#################

@app.route('/supermarkt/pfand', methods=['GET'])
@admin_required
def get_pfand_options():
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT pfand_id, amount, name, description FROM supermarkt_pfand")
                pfand_options = cursor.fetchall()
                pfand_list = [dict(p) for p in pfand_options]
        return jsonify({'pfand_options': pfand_list}), 200
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Pfand-Optionen: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der Pfand-Optionen'}), 500

@app.route('/supermarkt/pfand', methods=['POST'])
@admin_required
def add_pfand_option():
    data = request.get_json()
    amount = data.get('amount')
    name = data.get('name')
    description = data.get('description', '')

    if amount is None or not name:
        return jsonify({'error': 'Amount und Name sind erforderlich'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO supermarkt_pfand (amount, name, description)
                    VALUES (%s, %s, %s)
                    RETURNING pfand_id, amount, name, description
                """, (amount, name, description))
                new_pfand = cursor.fetchone()
                columns = [desc[0] for desc in cursor.description]
                new_pfand_dict = dict(zip(columns, new_pfand))
                conn.commit()
                return jsonify({'pfand_option': new_pfand_dict}), 201
    except Exception as e:
        logger.error(f"Fehler beim Hinzufügen der Pfand-Option: {e}")
        return jsonify({'error': 'Fehler beim Hinzufügen der Pfand-Option'}), 500

@app.route('/supermarkt/pfand/<int:pfand_id>', methods=['PUT'])
@admin_required
def update_pfand_option(pfand_id):
    data = request.get_json()
    amount = data.get('amount')
    name = data.get('name')
    description = data.get('description', '')

    if amount is None or not name:
        return jsonify({'error': 'Amount und Name sind erforderlich'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE supermarkt_pfand
                    SET amount = %s,
                        name = %s,
                        description = %s
                    WHERE pfand_id = %s
                    RETURNING pfand_id, amount, name, description
                """, (amount, name, description, pfand_id))
                updated_pfand = cursor.fetchone()
                if updated_pfand:
                    columns = [desc[0] for desc in cursor.description]
                    updated_pfand_dict = dict(zip(columns, updated_pfand))
                    conn.commit()
                    return jsonify({'pfand_option': updated_pfand_dict}), 200
                else:
                    return jsonify({'error': 'Pfand-Option nicht gefunden'}), 404
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren der Pfand-Option: {e}")
        return jsonify({'error': 'Fehler beim Aktualisieren der Pfand-Option'}), 500

@app.route('/supermarkt/pfand/<int:pfand_id>', methods=['DELETE'])
@admin_required
def delete_pfand_option(pfand_id):
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM supermarkt_pfand WHERE pfand_id = %s RETURNING pfand_id", (pfand_id,))
                deleted_pfand = cursor.fetchone()
                if deleted_pfand:
                    conn.commit()
                    return jsonify({'message': 'Pfand-Option erfolgreich gelöscht'}), 200
                else:
                    return jsonify({'error': 'Pfand-Option nicht gefunden'}), 404
    except Exception as e:
        logger.error(f"Fehler beim Löschen der Pfand-Option: {e}")
        return jsonify({'error': 'Fehler beim Löschen der Pfand-Option'}), 500





# Ergänze dies in deiner bestehenden Backend-Datei

@app.route('/mitarbeiter/read/qrcode/<token>', methods=['GET'])
def read_qrcode_mitarbeiter(token):
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
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
        logging.error(f"Fehler in read_qrcode: {e}")
        return jsonify({"error": "Interner Serverfehler"}), 500



if __name__ == '__main__':
    app.run(debug=True)