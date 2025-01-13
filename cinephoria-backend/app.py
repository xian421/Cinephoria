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



app = Flask(__name__, static_folder='public', static_url_path='')

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

# Datenbankkonfiguration
DATABASE_URL = os.getenv('DATABASE_URL')
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')
PAYPAL_API_BASE = 'https://api-m.sandbox.paypal.com'

# TMDb API-Konfiguration
TMDB_API_URL = "https://api.themoviedb.org/3/movie"
TMDB_BEARER_TOKEN = os.getenv('TMDB_BEARER_TOKEN')

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_BEARER_TOKEN}"
}

# SECRET_KEY definieren
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")

# Middleware für Token-Validierung
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token fehlt'}), 401
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = decoded  # Speichern Sie den Benutzer im Request-Objekt
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token abgelaufen'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Ungültiges Token'}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        user = request.user
        if user.get('role') != 'admin':
            return jsonify({'error': 'Zugriff verweigert - keine Admin-Rechte'}), 403
        return f(*args, **kwargs)
    return decorated

# PayPal Start


#Der Token ist richtig
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
    
    
@app.route('/paypal/create-order', methods=['POST'])
def create_paypal_order():
    data = request.get_json()
    total_amount = data.get('total_amount')

    if not total_amount:
        return jsonify({"error": "total_amount ist erforderlich"}), 400

    try:
        access_token = get_paypal_access_token()
        url = f"{PAYPAL_API_BASE}/v2/checkout/orders"
        
        # Bestimmte Felder im Body sind wichtig, z.B. amount, currency_code usw.
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
    
   
@app.route('/paypal/capture-order', methods=['POST'])
def capture_paypal_order():
    data = request.get_json()
    order_id = data.get('orderID')

    vorname = data.get('vorname')
    nachname = data.get('nachname')
    email = data.get('email')
    user_id = data.get('user_id')  # Kann None sein
    total_amount = data.get('total_amount')
    cart_items = data.get('cart_items', [])

    # Validierung
    if not order_id or not vorname or not nachname or not email or total_amount is None or not cart_items:
        return jsonify({"error": "Fehlende Buchungsdaten"}), 400

    try:
        # 1) PayPal Capture
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

        # 2) Prüfen, ob PayPal die Zahlung bestätigt hat
        if capture_data.get("status") == "COMPLETED":
            # 3) QR-Token generieren
            qr_token = str(uuid.uuid4())
            qr_seite = str(uuid.uuid4())

            # 4) Buchung in DB anlegen (inkl. qr_token)
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cursor:
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

                    conn.commit()

            return jsonify({
                "message": "Payment captured and booking completed",
                "booking_id": booking_id,
                "qr_token": qr_seite  # Gibt qr_seite zurück nicht qr_token
            }), 200
        else:
            # Wenn PayPal nicht COMPLETED ist, dann war etwas mit der Zahlung nicht in Ordnung
            return jsonify({"error": "Payment was not completed"}), 400

    except Exception as e:
        print("Fehler in capture_paypal_order:", e)
        return jsonify({"error": str(e)}), 500



# PayPal Ende
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
                    "qr_code": booking['qr_code'],
                    "movies": list(movies.values())  # Liste der Filme mit zugehörigen Sitzplätzen
                }

        return jsonify(booking_data), 200

    except Exception as e:
        logging.error(f"Fehler in read_qrcode: {e}")
        return jsonify({"error": "Interner Serverfehler"}), 500


# Token Validierung Endpunkt
@app.route('/validate-token', methods=['POST'])
def validate_token():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'error': 'Token fehlt'}), 401
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return jsonify({
            'user_id': decoded['user_id'],
            'first_name': decoded.get('first_name', ''),
            'last_name': decoded.get('last_name', ''),
            'initials': decoded.get('initials', ''),
            'role': decoded.get('role', '')
        }), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token abgelaufen'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Ungültiges Token'}), 401

@app.route('/movies/now_playing', methods=['GET'])
def get_now_playing():
    results = []
    for i in range(1, 6):  # Seiten von 1 bis 5 durchlaufen
        url = f"{TMDB_API_URL}/now_playing?language=de-DE&page={i}&region=DE"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            # Filter: Nur Filme mit einem gültigen `poster_path` hinzufügen
            filtered_results = [
                movie for movie in data['results'] if movie.get('poster_path')
            ]
            results.extend(filtered_results)
        else:
            print(f"Fehler bei Seite {i}: {response.status_code}")
    
    # Alle Ergebnisse in ein JSON-Objekt packen
    return jsonify({"results": results})

@app.route('/movies/upcoming', methods=['GET'])
def get_upcoming():
    url = f"{TMDB_API_URL}/upcoming?language=de-DE&page=1&region=DE"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Unable to fetch upcoming movies"}), response.status_code

@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    # URL für die TMDB-API mit der spezifischen Film-ID
    url = f"{TMDB_API_URL}/{movie_id}?language=de-DE"
    
    # Anfrage an die API senden
    response = requests.get(url, headers=HEADERS)
    
    # Erfolgreiche Antwort zurückgeben
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        # Fehler behandeln und Fehlermeldung zurückgeben
        return jsonify({"error": f"Unable to fetch details for movie ID {movie_id}"}), response.status_code

@app.route('/movie/<int:movie_id>/release_dates', methods=['GET'])
def get_movie_release_dates(movie_id):
    # URL für die TMDB-API mit der spezifischen Film-ID
    url = f"{TMDB_API_URL}/{movie_id}/release_dates"
    
    # Anfrage an die API senden
    response = requests.get(url, headers=HEADERS)
    
    # Erfolgreiche Antwort zurückgeben
    if response.status_code == 200:
        # JSON-Antwort parsen
        data = response.json()
        
        # Filtere nur den Eintrag mit 'iso_3166_1': 'DE'
        german_release = next((item for item in data['results'] if item['iso_3166_1'] == 'DE'), None)
        
        if german_release:
            return jsonify(german_release)
        else:
            return jsonify({"error": "No release date found for Germany (DE)"}), 404
    else:
        # Fehler behandeln und Fehlermeldung zurückgeben
        return jsonify({"error": f"Unable to fetch details for movie ID {movie_id}"}), response.status_code

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'E-Mail und Passwort sind erforderlich'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, password, vorname, nachname, role FROM users WHERE email = %s", (email,))
                result = cursor.fetchone()

                if not result:
                    return jsonify({'error': 'Ungültige E-Mail oder Passwort'}), 401

                user_id, stored_password, vorname, nachname, role = result

                cursor.execute("SELECT crypt(%s, %s) = %s AS password_match", (password, stored_password, stored_password))
                is_valid = cursor.fetchone()[0]

                if is_valid:
                    initials = f"{vorname[0].upper()}{nachname[0].upper()}"
                    token = jwt.encode({
                        'user_id': user_id,
                        'first_name': vorname,
                        'last_name': nachname,
                        'initials': initials,
                        'role': role,  
                        'exp': datetime.now(timezone.utc) + timedelta(hours=1)
                    }, SECRET_KEY, algorithm='HS256')

                    return jsonify({
                        'message': 'Login erfolgreich',
                        'token': token,
                        'first_name': vorname,
                        'last_name': nachname,
                        'initials': initials,
                        'role': role
                    }), 200
                else:
                    return jsonify({'error': 'Ungültige E-Mail oder Passwort'}), 401

    except Exception as e:
        print(f"Fehler: {e}")
        return jsonify({'error': 'Fehler bei der Anmeldung'}), 500

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

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    vorname = data.get('first_name')  # Mapping von "first_name" auf "vorname"
    nachname = data.get('last_name')  # Mapping von "last_name" auf "nachname"
    email = data.get('email')
    password = data.get('password')

    if not vorname or not nachname or not email or not password:
        return jsonify({'error': 'Alle Felder sind erforderlich'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                # Prüfen, ob der Benutzer schon existiert
                cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    return jsonify({'error': 'Benutzer mit dieser E-Mail existiert bereits'}), 409

                # Passwort hashen mit der PostgreSQL-Methode
                cursor.execute(
                    "INSERT INTO users (vorname, nachname, email, password) VALUES (%s, %s, %s, crypt(%s, gen_salt('bf')))",
                    (vorname, nachname, email, password),
                )
        return jsonify({'message': 'Registrierung erfolgreich'}), 201

    except Exception as e:
        print(f"Fehler bei der Registrierung: {e}")
        return jsonify({'error': 'Ein Fehler ist aufgetreten'}), 500

@app.route('/seats', methods=['POST'])
@admin_required
def create_seat():
    data = request.get_json()
    screen_id = data.get('screen_id')
    row = data.get('row')
    number = data.get('number')
    seat_type_name = data.get('type', 'standard')

    if not screen_id or not row or not number:
        return jsonify({'error': 'screen_id, row und number sind erforderlich'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                # Sitztyp-ID basierend auf dem Namen abrufen
                cursor.execute("""
                    SELECT seat_type_id FROM seat_types WHERE name = %s
                """, (seat_type_name,))
                result = cursor.fetchone()
                if not result:
                    return jsonify({'error': 'Ungültiger Sitztyp'}), 400
                seat_type_id = result[0]

                # Prüfen, ob der Sitz bereits existiert
                cursor.execute("""
                    SELECT seat_id FROM seats
                    WHERE screen_id = %s AND row = %s AND number = %s
                """, (screen_id, row, number))
                existing_seat = cursor.fetchone()
                if existing_seat:
                    return jsonify({'error': 'Sitz existiert bereits'}), 400

                # Sitz einfügen mit seat_type_id
                cursor.execute("""
                    INSERT INTO seats (screen_id, row, number, seat_type_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING seat_id
                """, (screen_id, row, number, seat_type_id))

                seat_id = cursor.fetchone()[0]

        return jsonify({'message': 'Sitz erstellt', 'seat_id': seat_id}), 201

    except Exception as e:
        print(f"Fehler beim Erstellen des Sitzes: {e}")
        return jsonify({'error': 'Fehler beim Erstellen des Sitzes'}), 500

@app.route('/seats/<int:seat_id>', methods=['DELETE'])
@admin_required
def delete_seat(seat_id):
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM seats
                    WHERE seat_id = %s
                """, (seat_id,))
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Sitz nicht gefunden'}), 404

        return jsonify({'message': 'Sitz gelöscht'}), 200

    except Exception as e:
        print(f"Fehler beim Löschen des Sitzes: {e}")
        return jsonify({'error': 'Fehler beim Löschen des Sitzes'}), 500

@app.route('/seats', methods=['DELETE'])
@admin_required
def delete_all_seats():
    screen_id = request.args.get('screen_id')
    if not screen_id:
        return jsonify({'error': 'Screen ID ist erforderlich'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM seats
                    WHERE screen_id = %s
                """, (screen_id,))
                # rowcount kann ignoriert werden, da wir alle Sitze löschen

        return jsonify({'message': 'Alle Sitze gelöscht'}), 200
    except Exception as e:
        print(f"Fehler beim Löschen aller Sitze: {e}")
        return jsonify({'error': 'Fehler beim Löschen aller Sitze'}), 500

@app.route('/seats', methods=['GET'])
def get_seats():
    screen_id = request.args.get('screen_id')
    if not screen_id:
        return jsonify({'error': 'screen_id ist erforderlich'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT s.seat_id, s.screen_id, s.row, s.number, st.name AS seat_type_name, st.price
                    FROM seats s
                    JOIN seat_types st ON s.seat_type_id = st.seat_type_id
                    WHERE s.screen_id = %s
                """, (screen_id,))
                seats = cursor.fetchall()
                seats_list = [
                    {
                        'seat_id': seat[0],
                        'screen_id': seat[1],
                        'row': seat[2],
                        'number': seat[3],
                        'type': seat[4],  # seat_type_name
                        'price': float(seat[5])
                    } for seat in seats
                ]

        return jsonify({'seats': seats_list}), 200

    except Exception as e:
        print(f"Fehler beim Abrufen der Sitze: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der Sitze'}), 500


# Neuer Endpunkt zum Abrufen eines spezifischen Sitzes anhand der seat_id SucheDis
@app.route('/seats/<seat_id>', methods=['GET'])
def get_seat(seat_id):
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                SELECT s.seat_id
                     , s.screen_id
                     , s.row
                     , s.number
                     , st.name AS seat_type_name
                     , st.price
                     , st.seat_type_id
                FROM seats s
                JOIN seat_types st ON s.seat_type_id = st.seat_type_id
                WHERE s.seat_id = %s
                """, (seat_id,))
                seat = cursor.fetchone()
                
                if seat:
                    seat_details = {
                        'seat_id': seat[0],
                        'screen_id': seat[1],
                        'row': seat[2],
                        'number': seat[3],
                        'type': seat[4],  # seat_type_name
                        'price': float(seat[5]),
                        'seat_type_id': seat[6]
                    }
                    return jsonify({'seat': seat_details}), 200
                else:
                    return jsonify({'error': 'Sitz nicht gefunden'}), 404

    except Exception as e:
        print(f"Fehler beim Abrufen des Sitzes: {e}")
        return jsonify({'error': 'Fehler beim Abrufen des Sitzes'}), 500



@app.route('/seat_types', methods=['GET'])
def get_seat_types():
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT seat_type_id, name, price, color, icon
                    FROM seat_types
                """)
                seat_types = cursor.fetchall()
                seat_types_list = [
                    {
                        'seat_type_id': st[0],
                        'name': st[1],
                        'price': float(st[2]),
                        'color': st[3] or '#678be0',  # Default color if None
                        'icon': st[4]
                    } for st in seat_types
                ]
        return jsonify({'seat_types': seat_types_list}), 200
    except Exception as e:
        print(f"Fehler beim Abrufen der Sitztypen: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der Sitztypen'}), 500


@app.route('/showtimes', methods=['POST'])
@admin_required
def create_showtime():
    data = request.get_json()
    screen_id = data.get('screen_id')
    movie_id = data.get('movie_id')
    start_time = data.get('start_time')
    end_time = data.get('end_time')  # Optional

    if not all([screen_id, movie_id, start_time]):
        return jsonify({'error': 'Alle erforderlichen Felder müssen ausgefüllt sein'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO showtimes (movie_id, screen_id, start_time, end_time)
                    VALUES (%s, %s, %s, %s)
                    RETURNING showtime_id
                """, (movie_id, screen_id, start_time, end_time))
                showtime_id = cursor.fetchone()[0]

        return jsonify({'message': 'Showtime erstellt', 'showtime_id': showtime_id}), 201
    except Exception as e:
        print(f"Fehler beim Erstellen des Showtimes: {e}")
        return jsonify({'error': 'Fehler beim Erstellen des Showtimes'}), 500

@app.route('/showtimes', methods=['GET'])
def get_showtimes():
    screen_id = request.args.get('screen_id')  # Optional: Filter nach Screen
    movie_id = request.args.get('movie_id')    # Optional: Filter nach Movie
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT s.showtime_id, s.movie_id, s.screen_id, s.start_time, s.end_time, sc.name as screen_name
                    FROM showtimes s
                    JOIN screens sc ON s.screen_id = sc.screen_id
                """
                params = []
                conditions = []
                if screen_id:
                    conditions.append("screen_id = %s")
                    params.append(screen_id)
                if movie_id:
                    conditions.append("movie_id = %s")
                    params.append(movie_id)
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                query += " ORDER BY start_time"
                cursor.execute(query, tuple(params))
                showtimes = cursor.fetchall()
                # Strukturieren der Daten als Liste von Dictionaries
                showtimes_list = [{
                    'showtime_id': row[0],
                    'movie_id': row[1],
                    'screen_id': row[2],
                    'start_time': row[3].isoformat(),
                    'end_time': row[4].isoformat() if row[4] else None,
                    'screen_name': row[5]
                } for row in showtimes]
        return jsonify({'showtimes': showtimes_list}), 200
    except Exception as e:
        print(f"Fehler beim Abrufen der Showtimes: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der Showtimes'}), 500
    
  
@app.route('/showtimes/aktuell', methods=['GET'])
def get_showtimes_today():
    movie_id = request.args.get('movie_id')  # Optionaler Parameter
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT s.showtime_id, s.movie_id, s.screen_id, s.start_time, s.end_time, sc.name as screen_name
                    FROM showtimes s
                    JOIN screens sc ON s.screen_id = sc.screen_id
                    WHERE s.start_time >= DATE_TRUNC('day', NOW())
                """
                params = []
                if movie_id:
                    query += " AND s.movie_id = %s"
                    params.append(movie_id)
                query += " ORDER BY s.start_time"
                cursor.execute(query, tuple(params))
                showtimes = cursor.fetchall()
                # Strukturieren der Daten als Liste von Dictionaries
                showtimes_list = [{
                    'showtime_id': row[0],
                    'movie_id': row[1],
                    'screen_id': row[2],
                    'start_time': row[3].isoformat(),
                    'end_time': row[4].isoformat() if row[4] else None,
                    'screen_name': row[5]
                } for row in showtimes]
        return jsonify({'showtimes': showtimes_list}), 200
    except Exception as e:
        print(f"Fehler beim Abrufen der Showtimes: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der Showtimes'}), 500

    


@app.route('/showtimes/<int:showtime_id>', methods=['PUT'])
@admin_required
def update_showtime(showtime_id):
    data = request.get_json()
    screen_id = data.get('screen_id')
    movie_id = data.get('movie_id')
    start_time = data.get('start_time')
    end_time = data.get('end_time')  # Optional

    if not all([screen_id, movie_id, start_time]):
        return jsonify({'error': 'Alle erforderlichen Felder müssen ausgefüllt sein'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE showtimes
                    SET movie_id = %s,
                        screen_id = %s,
                        start_time = %s,
                        end_time = %s
                    WHERE showtime_id = %s
                """, (movie_id, screen_id, start_time, end_time, showtime_id))
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Showtime nicht gefunden'}), 404
        return jsonify({'message': 'Showtime aktualisiert'}), 200
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Showtimes: {e}")
        return jsonify({'error': 'Fehler beim Aktualisieren des Showtimes'}), 500

@app.route('/bookings', methods=['POST']) #Dashierändern
@token_required
def create_booking_route():
    data = request.get_json()
    showtime_id = data.get('showtime_id')
    seat_ids = data.get('seat_ids')  # Liste von seat_id
    user_id = request.user.get('user_id')  # Aus dem Token
    order_id = data.get('order_id')  # Neue PayPal Order ID

    if not showtime_id or not seat_ids or not order_id:
        return jsonify({'error': 'showtime_id, seat_ids und order_id sind erforderlich'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                # Beginne eine Transaktion
                cursor.execute("BEGIN;")
                
                # Ermitteln des Kinosaals für die Showtime
                cursor.execute("""
                    SELECT screen_id FROM showtimes WHERE showtime_id = %s
                """, (showtime_id,))
                screen = cursor.fetchone()
                if not screen:
                    conn.rollback()
                    return jsonify({'error': 'Showtime nicht gefunden'}), 404
                screen_id = screen[0]
                
                # Überprüfen, ob die Sitzplätze zur Showtime gehören und verfügbar sind
                cursor.execute("""
                    SELECT seat_id FROM seats
                    WHERE seat_id = ANY(%s) AND screen_id = %s
                """, (seat_ids, screen_id))
                available_seats = {row[0] for row in cursor.fetchall()}
                
                if not available_seats.issuperset(set(seat_ids)):
                    conn.rollback()
                    return jsonify({'error': 'Ein oder mehrere Sitzplätze sind nicht verfügbar'}), 400
                
                # Überprüfen, ob die Sitzplätze bereits gebucht wurden
                cursor.execute("""
                    SELECT bs.seat_id FROM booking_seats bs
                    JOIN bookings b ON bs.booking_id = b.booking_id
                    WHERE bs.showtime_id = %s AND b.payment_status = 'completed' AND bs.seat_id = ANY(%s)
                    FOR UPDATE
                """, (showtime_id, seat_ids))
                already_booked = {row[0] for row in cursor.fetchall()}
                
                if already_booked:
                    conn.rollback()
                    return jsonify({'error': 'Ein oder mehrere Sitzplätze sind bereits gebucht'}), 400
                
                # Preise für die ausgewählten Sitzplätze abrufen
                cursor.execute("""
                    SELECT s.seat_id, st.price
                    FROM seats s
                    JOIN seat_types st ON s.seat_type_id = st.seat_type_id
                    WHERE s.seat_id = ANY(%s)
                """, (seat_ids,))
                seat_prices = cursor.fetchall()
                seat_price_dict = {seat_id: price for seat_id, price in seat_prices}
                
                # Gesamtbetrag berechnen
                total_amount = sum(seat_price_dict[seat_id] for seat_id in seat_ids)
                
                # Erstellen der Buchung
                cursor.execute("""
                    INSERT INTO bookings (user_id, showtime_id, payment_status, total_amount, paypal_order_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING booking_id
                """, (user_id, showtime_id, 'completed', total_amount, order_id))
                booking_id = cursor.fetchone()[0]
                
                # Verknüpfen der Sitzplätze mit der Buchung und deren Preis
                for seat_id in seat_ids:
                    price = seat_price_dict[seat_id]
                    cursor.execute("""
                        INSERT INTO booking_seats (booking_id, seat_id, price)
                        VALUES (%s, %s, %s)
                    """, (booking_id, seat_id, price))
                
                # **Neuer Code: Punkte gutschreiben**
                points_to_add = int(total_amount)  # 1 Euro = 1 Punkt

                # Aktualisiere user_points
                cursor.execute("""
                    UPDATE user_points
                    SET points = points + %s,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                """, (points_to_add, user_id))

                # Protokolliere die Punkte-Transaktion
                cursor.execute("""
                    INSERT INTO points_transactions (user_id, points_change, description)
                    VALUES (%s, %s, %s)
                """, (user_id, points_to_add, f'Punkte für Buchung {booking_id}'))

                # Commit der Transaktion
                conn.commit()
        
        return jsonify({'message': 'Buchung erfolgreich', 'booking_id': booking_id}), 201
    except Exception as e:
        print(f"Fehler beim Erstellen der Buchung: {e}")
        return jsonify({'error': 'Fehler beim Erstellen der Buchung'}), 500

@app.route('/showtimes/<int:showtime_id>/seats', methods=['GET'])
def get_seats_for_showtime(showtime_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    guest_id = request.args.get('guest_id', None)
    user_id = None

    # Versuch den Token zu dekodieren, um user_id zu erhalten
    if token:
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = decoded['user_id']
        except jwt.ExpiredSignatureError:
            pass
        except jwt.InvalidTokenError:
            pass

    # user_id hat Vorrang (wenn token gültig), sonst guest_id verwenden
    # Wenn beides None ist, ist der Nutzer anonym ohne guest_id (sollte eigentlich nicht passieren, da guest_id immer generiert wird)
    
    # Zuerst abgelaufene Reservierungen löschen
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
           # cursor.execute("DELETE FROM guest_cart_items WHERE reserved_until < NOW()")
            #cursor.execute("DELETE FROM user_cart_items WHERE reserved_until < NOW()")
            print('Test')

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # Showtime -> screen_id ermitteln
                cursor.execute("SELECT screen_id FROM showtimes WHERE showtime_id = %s", (showtime_id,))
                screen = cursor.fetchone()
                if not screen:
                    return jsonify({'error': 'Showtime nicht gefunden'}), 404
                screen_id = screen['screen_id']

                # Alle Sitzplätze für diesen Kinosaal holen
                cursor.execute("""
                    SELECT s.seat_id, s.row, s.number, st.name AS seat_type_name, st.price, st.color, st.icon, scr.name AS screen_name
                    FROM seats s
                    JOIN seat_types st ON s.seat_type_id = st.seat_type_id
                    JOIN screens scr ON s.screen_id = scr.screen_id
                    WHERE s.screen_id = %s
                    ORDER BY s.row, s.number
                """, (screen_id,))
                all_seats = cursor.fetchall()

                # Bereits gebuchte Sitzplätze (booking_seats, payment_status=completed)
                cursor.execute("""
                    SELECT bs.seat_id 
                    FROM booking_seats bs
                    WHERE bs.showtime_id = %s 
                """, (showtime_id,)) # AND b.payment_status = 'completed'
                booked_seats = {row['seat_id'] for row in cursor.fetchall()}

                # Reservierte Sitzplätze in user_carts
                cursor.execute("""
                    SELECT uci.seat_id, uci.user_id, uc.valid_until
                    FROM user_cart_items uci
                    JOIN user_carts uc ON uci.user_id = uc.user_id
                    WHERE uci.showtime_id = %s 
                """, (showtime_id,))
                user_reserved = cursor.fetchall()

                # Reservierte Sitzplätze in guest_carts
                cursor.execute("""
                    SELECT gci.seat_id, gci.guest_id, gc.valid_until
                    FROM guest_cart_items gci
                    JOIN guest_carts gc ON gci.guest_id = gc.guest_id
                    WHERE gci.showtime_id = %s
                """, (showtime_id,))
                guest_reserved = cursor.fetchall()

                # Sets für Reserved Seats erstellen
                reserved_by_others = set()
                reserved_by_self = set()

                # Alle User-Reservierungen durchgehen
                for r in user_reserved:
                    sid = r['seat_id']
                    uid = r['user_id']
                    if user_id and uid == user_id:
                        # Gehört dem aktuellen eingeloggten User
                        reserved_by_self.add(sid)
                    else:
                        reserved_by_others.add(sid)

                # Alle Gast-Reservierungen durchgehen
                for r in guest_reserved:
                    sid = r['seat_id']
                    gid = r['guest_id']
                    if guest_id and gid == guest_id and not user_id:
                        # Gehört diesem Gast (nicht eingeloggt)
                        reserved_by_self.add(sid)
                    else:
                        reserved_by_others.add(sid)

                seats_list = []
                for seat in all_seats:
                    sid = seat['seat_id']
                    # Reihenfolge der Checks:
                    # 1. Bereits gebucht -> unavailable
                    # 2. Von anderen reserviert -> unavailable
                    # 3. Vom Nutzer selbst reserviert -> verfügbar aber reserved_by_self=true
                    # 4. Sonst available

                    if sid in booked_seats:
                        status = 'unavailable'
                        rbs = False
                    elif sid in reserved_by_others:
                        status = 'unavailable'
                        rbs = False
                    elif sid in reserved_by_self:
                        # Sitzplatz gehört dem aktuellen User/Gast
                        status = 'available'
                        rbs = True
                    else:
                        status = 'available'
                        rbs = False

                    seats_list.append({
                        'seat_id': sid,
                        'row': seat['row'],
                        'number': seat['number'],
                        'type': seat['seat_type_name'],
                        'price': float(seat['price']),
                        'color': seat['color'] or '#678be0',
                        'icon': seat['icon'],
                        'status': status,
                        'reserved_by_self': rbs,
                        'screen_name': seat['screen_name']
                    })
                    
        return jsonify({'seats': seats_list}), 200
    except Exception as e:
        print(f"Fehler beim Abrufen der Sitzplätze: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der Sitzplätze'}), 500


def get_allowed_profile_images():
    PROFILE_IMAGES_DIR = os.path.join(app.static_folder, 'Profilbilder')
    try:
        images = [f for f in os.listdir(PROFILE_IMAGES_DIR) if os.path.isfile(os.path.join(PROFILE_IMAGES_DIR, f))]
        print(f"Gefundene Profilbilder: {images}")  # Logge die gefundenen Bilder
        return images
    except Exception as e:
        print(f"Fehler beim Abrufen der Profilbilder: {e}")
        return []

@app.route('/profile', methods=['GET', 'PUT'])
@token_required
def profile():
    user_id = request.user.get('user_id')

    if request.method == 'GET':
        try:
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT vorname, nachname, email, role, profile_image, nickname 
                        FROM users 
                        WHERE id = %s
                    """, (user_id,))
                    result = cursor.fetchone()
                    if not result:
                        return jsonify({'error': 'Benutzer nicht gefunden'}), 404
                    vorname, nachname, email, role, profile_image, nickname = result
                    return jsonify({
                        'vorname': vorname,
                        'nachname': nachname,
                        'email': email,
                        'role': role,
                        'profile_image': profile_image,
                        'nickname': nickname
                    }), 200
        except Exception as e:
            print(f"Fehler beim Abrufen des Profils: {e}")
            return jsonify({'error': 'Fehler beim Abrufen des Profils'}), 500

    elif request.method == 'PUT':
        data = request.get_json()
        vorname = data.get('vorname')
        nachname = data.get('nachname')
        email = data.get('email')
        nickname = data.get('nickname')
        role = data.get('role')

        if not vorname or not nachname or not email:
            return jsonify({'error': 'Alle Felder sind erforderlich'}), 400

        try:
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE users 
                        SET vorname = %s, nachname = %s, email = %s, nickname = %s, role = %s
                        WHERE id = %s
                    """, (vorname, nachname, email, nickname, role, user_id))
                    conn.commit()
            return jsonify({'message': 'Profil aktualisiert'}), 200
        except Exception as e:
            print(f"Fehler beim Aktualisieren des Profils: {e}")
            return jsonify({'error': 'Fehler beim Aktualisieren des Profils'}), 500

# Neuer Endpunkt zum Aktualisieren des Profilbildes
@app.route('/profile/image', methods=['PUT'])
@token_required
def update_profile_image():
    user_id = request.user.get('user_id')
    data = request.get_json()
    if not data or 'profile_image' not in data:
        return jsonify({'error': 'Keine Bilddaten erhalten'}), 400
    profile_image = data['profile_image']
    
    # Validierung des Profilbildes
    allowed_images = get_allowed_profile_images()
    if profile_image not in allowed_images:
        return jsonify({'error': 'Ungültiges Profilbild'}), 400
    
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE users SET profile_image = %s WHERE id = %s", (profile_image, user_id))
                conn.commit()
        return jsonify({'message': 'Profilbild aktualisiert'}), 200
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Profilbildes: {e}")
        return jsonify({'error': 'Fehler beim Aktualisieren des Profilbildes'}), 500

# Neuer Endpunkt zum Auflisten der verfügbaren Profilbilder
@app.route('/profile/images', methods=['GET'])
@token_required
def list_profile_images():
    try:
        images = get_allowed_profile_images()
        return jsonify({'images': images}), 200
    except Exception as e:
        print(f"Fehler beim Auflisten der Profilbilder: {e}")
        return jsonify({'error': 'Fehler beim Auflisten der Profilbilder'}), 500

@app.route('/seats/batch_update', methods=['POST'])
@admin_required
def batch_update_seats():
    data = request.get_json()
    screen_id = data.get('screen_id')
    seats_to_add = data.get('seats_to_add', [])
    seats_to_delete = data.get('seats_to_delete', [])
    seats_to_update = data.get('seats_to_update', [])

    if not screen_id:
        return jsonify({'error': 'screen_id ist erforderlich'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                # Beginne eine Transaktion
                cursor.execute("BEGIN;")
                
                # Hinzufügen der Sitze in Bulk
                if seats_to_add:
                    values = []
                    for seat in seats_to_add:
                        seat_type_name = seat.get('type', 'standard')
                        # Sitztyp-ID abrufen
                        cursor.execute("SELECT seat_type_id FROM seat_types WHERE name = %s", (seat_type_name,))
                        result = cursor.fetchone()
                        if not result:
                            conn.rollback()
                            return jsonify({'error': f'Ungültiger Sitztyp: {seat_type_name}'}), 400
                        seat_type_id = result[0]
                        values.append((screen_id, seat['row'], seat['number'], seat_type_id))
                    insert_query = """
                        INSERT INTO seats (screen_id, row, number, seat_type_id)
                        VALUES %s
                        ON CONFLICT (screen_id, row, number) DO NOTHING
                    """
                    psycopg2.extras.execute_values(cursor, insert_query, values)

                # Aktualisieren der Sitztypen in Bulk
                if seats_to_update:
                    for seat in seats_to_update:
                        seat_type_name = seat.get('type', 'standard')
                        # Sitztyp-ID abrufen
                        cursor.execute("SELECT seat_type_id FROM seat_types WHERE name = %s", (seat_type_name,))
                        result = cursor.fetchone()
                        if not result:
                            conn.rollback()
                            return jsonify({'error': f'Ungültiger Sitztyp: {seat_type_name}'}), 400
                        seat_type_id = result[0]
                        cursor.execute("""
                            UPDATE seats
                            SET seat_type_id = %s
                            WHERE screen_id = %s AND row = %s AND number = %s
                        """, (seat_type_id, screen_id, seat['row'], seat['number']))

                # Löschen der Sitze in Bulk
                if seats_to_delete:
                    delete_query = """
                        DELETE FROM seats
                        WHERE screen_id = %s AND (row, number) IN %s
                    """
                    # Erstelle eine Liste von Tupeln (row, number)
                    seats_to_delete_tuples = [(seat['row'], seat['number']) for seat in seats_to_delete]
                    cursor.execute(delete_query, (screen_id, tuple(seats_to_delete_tuples)))

                # Commit der Transaktion
                conn.commit()

        return jsonify({
            'message': 'Sitze erfolgreich aktualisiert',
            'added': len(seats_to_add),
            'deleted': len(seats_to_delete),
            'updated': len(seats_to_update)
        }), 200

    except Exception as e:
        print(f"Fehler beim Aktualisieren der Sitze: {e}")
        return jsonify({'error': 'Fehler beim Aktualisieren der Sitze'}), 500

@app.route('/seat_types', methods=['POST'])
@admin_required
def add_seat_type():
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    color = data.get('color')  # New field
    icon = data.get('icon')    # New field

    if not (name and price is not None and color):
        return jsonify({'error': 'Name, Preis und Farbe sind erforderlich'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO seat_types (name, price, color, icon) VALUES (%s, %s, %s, %s) RETURNING seat_type_id",
                    (name, price, color, icon)
                )
                seat_type_id = cursor.fetchone()[0]
                conn.commit()
                return jsonify({'message': 'Sitztyp hinzugefügt', 'seat_type_id': seat_type_id}), 201
    except Exception as e:
        print(f"Fehler beim Hinzufügen des Sitztyps: {e}")
        return jsonify({'error': 'Fehler beim Hinzufügen des Sitztyps'}), 500


@app.route('/seat_types/<int:seat_type_id>', methods=['PUT'])
@admin_required
def update_seat_type(seat_type_id):
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    color = data.get('color')  # New field
    icon = data.get('icon')    # New field

    #if not all([name, (price is not None), color]):
    if price is None or color is None or not name:
        return jsonify({'error': f'Alle Felder müssen angegeben werden. Name: {name}, Price: {price}, Color: {color}'}), 400



    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                # Build the UPDATE statement dynamically
                update_fields = []
                update_values = []

                if name:
                    update_fields.append("name = %s")
                    update_values.append(name)
                if price is not None:
                    update_fields.append("price = %s")
                    update_values.append(price)
                if color:
                    update_fields.append("color = %s")
                    update_values.append(color)

                update_fields.append("icon = %s")
                update_values.append(icon)

                update_values.append(seat_type_id)

                update_query = f"UPDATE seat_types SET {', '.join(update_fields)} WHERE seat_type_id = %s"
                cursor.execute(update_query, tuple(update_values))

                if cursor.rowcount == 0:
                    return jsonify({'error': 'Sitztyp nicht gefunden'}), 404

                conn.commit()
                return jsonify({'message': 'Sitztyp aktualisiert'}), 200
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Sitztyps: {e}")
        return jsonify({'error': 'Fehler beim Aktualisieren des Sitztyps'}), 500

@app.route('/seat_types/<int:seat_type_id>', methods=['DELETE'])
@admin_required
def delete_seat_type(seat_type_id):
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM seat_types
                    WHERE seat_type_id = %s
                """, (seat_type_id,))
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Sitztyp nicht gefunden'}), 404

        return jsonify({'message': 'Sitztyp gelöscht'}), 200

    except Exception as e:
        print(f"Fehler beim Löschen des Sitzes: {e}")
        return jsonify({'error': 'Fehler beim Löschen des Sitzes'}), 500


@app.route('/user/cart', methods=['GET'])
@token_required
def get_user_cart():
    clear_expired_user_cart_items()
    user_id = request.user.get('user_id')
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
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





@app.route('/user/cart/<int:showtime_id>/<int:seat_id>', methods=['DELETE'])
@token_required
def remove_from_user_cart(showtime_id, seat_id):
    clear_expired_user_cart_items()
    user_id = request.user.get('user_id')
    
    if not showtime_id:
        return jsonify({'error': 'showtime_id ist erforderlich'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
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


@app.route('/user/cart', methods=['DELETE'])
@token_required
def clear_user_cart():
    user_id = request.user.get('user_id')
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
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


def clear_expired_guest_cart_items():
    with psycopg2.connect(DATABASE_URL) as conn:
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

def clear_expired_user_cart_items():
    with psycopg2.connect(DATABASE_URL) as conn:
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

@app.route('/user/cart', methods=['POST'])
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
        with psycopg2.connect(DATABASE_URL) as conn:
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



@app.route('/guest/cart', methods=['GET'])
def get_guest_cart():
    clear_expired_guest_cart_items()  # Erst abgelaufene Einträge bereinigen
    guest_id = request.args.get('guest_id', None)
    if not guest_id:
        return jsonify({'error': 'guest_id ist erforderlich'}), 400
    
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
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


@app.route('/guest/cart', methods=['POST'])
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
        with psycopg2.connect(DATABASE_URL) as conn:
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
        logger.error(f"IntegrityError beim Hinzufügen zum Guest-Warenkorb: {ie}")
        return jsonify({'error': 'Der Sitzplatz ist bereits reserviert'}), 409
    except Exception as e:
        logger.error(f"Fehler beim Hinzufügen zum Guest-Warenkorb: {e}")
        return jsonify({'error': 'Fehler beim Hinzufügen zum Guest-Warenkorb'}), 500

    

@app.route('/guest/cart/<int:showtime_id>/<int:seat_id>', methods=['DELETE'])
def remove_from_guest_cart(showtime_id, seat_id):
    clear_expired_guest_cart_items()
    guest_id = request.args.get('guest_id', None)

    if not guest_id or not showtime_id:
        return jsonify({'error': 'guest_id und showtime_id sind erforderlich'}), 400
    
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
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


@app.route('/guest/cart', methods=['DELETE'])
def clear_guest_cart():
    clear_expired_guest_cart_items()
    guest_id = request.args.get('guest_id', None)
    if not guest_id:
        return jsonify({'error': 'guest_id ist erforderlich'}), 400
    
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
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

@app.route('/discounts', methods=['GET'])
def get_discounts():
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT discount_id, name, description FROM discounts")
                discounts = cursor.fetchall()
                discounts_list = [dict(d) for d in discounts]
        return jsonify({'discounts': discounts_list}), 200
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Discounts: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der Discounts'}), 500

    

@app.route('/discounts', methods=['POST'])
@admin_required
def add_discount():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')

    if not name:
        return jsonify({'error': 'Name ist erforderlich'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO discounts (name, description) VALUES (%s, %s) RETURNING discount_id",
                    (name, description)
                )
                discount_id = cursor.fetchone()[0]
                conn.commit()
                return jsonify({'message': 'Discount hinzugefügt', 'discount_id': discount_id}), 201
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'error': 'Discount mit diesem Namen existiert bereits'}), 409
    except Exception as e:
        logger.error(f"Fehler beim Hinzufügen des Discounts: {e}")
        return jsonify({'error': 'Fehler beim Hinzufügen des Discounts'}), 500
    
        
@app.route('/discounts/<int:discount_id>', methods=['PUT'])
@admin_required
def update_discount(discount_id):
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')

    if not name:
        return jsonify({'error': 'Name ist erforderlich'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE discounts
                    SET name = %s,
                        description = %s
                    WHERE discount_id = %s
                """, (name, description, discount_id))
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Discount nicht gefunden'}), 404
                conn.commit()
                return jsonify({'message': 'Discount aktualisiert'}), 200
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'error': 'Ein Discount mit diesem Namen existiert bereits'}), 409
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren des Discounts: {e}")
        return jsonify({'error': 'Fehler beim Aktualisieren des Discounts'}), 500
    

@app.route('/discounts/<int:discount_id>', methods=['DELETE'])
@admin_required
def delete_discount(discount_id):
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM discounts WHERE discount_id = %s", (discount_id,))
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Discount nicht gefunden'}), 404
                conn.commit()
                return jsonify({'message': 'Discount gelöscht'}), 200
    except Exception as e:
        logger.error(f"Fehler beim Löschen des Discounts: {e}")
        return jsonify({'error': 'Fehler beim Löschen des Discounts'}), 500
    

@app.route('/seat_type_discounts', methods=['POST'])
@admin_required
def assign_discount_to_seat_type():
    data = request.get_json()
    seat_type_id = data.get('seat_type_id')
    discount_id = data.get('discount_id')
    discount_amount = data.get('discount_amount')
    discount_percentage = data.get('discount_percentage')

    if not seat_type_id or not discount_id:
        return jsonify({'error': 'seat_type_id und discount_id sind erforderlich'}), 400

    if discount_amount is None and discount_percentage is None:
        return jsonify({'error': 'Entweder discount_amount oder discount_percentage muss angegeben werden'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                # Überprüfen, ob seat_type_id und discount_id existieren
                cursor.execute("SELECT seat_type_id FROM seat_types WHERE seat_type_id = %s", (seat_type_id,))
                if not cursor.fetchone():
                    return jsonify({'error': 'Ungültiger seat_type_id'}), 400

                cursor.execute("SELECT discount_id FROM discounts WHERE discount_id = %s", (discount_id,))
                if not cursor.fetchone():
                    return jsonify({'error': 'Ungültiger discount_id'}), 400

                # Insert oder Update
                cursor.execute("""
                    INSERT INTO seat_type_discounts (seat_type_id, discount_id, discount_amount, discount_percentage)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (seat_type_id, discount_id) 
                    DO UPDATE SET 
                        discount_amount = EXCLUDED.discount_amount,
                        discount_percentage = EXCLUDED.discount_percentage
                """, (seat_type_id, discount_id, discount_amount, discount_percentage))
                conn.commit()
                return jsonify({'message': 'Discount dem Sitztyp zugewiesen'}), 200
    except Exception as e:
        logger.error(f"Fehler beim Zuweisen des Discounts zu Sitztyp: {e}")
        return jsonify({'error': 'Fehler beim Zuweisen des Discounts zu Sitztyp'}), 500


@app.route('/seat_type_discounts', methods=['DELETE'])
@admin_required
def remove_discount_from_seat_type():
    data = request.get_json()
    seat_type_id = data.get('seat_type_id')
    discount_id = data.get('discount_id')

    if not seat_type_id or not discount_id:
        return jsonify({'error': 'seat_type_id und discount_id sind erforderlich'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM seat_type_discounts
                    WHERE seat_type_id = %s AND discount_id = %s
                """, (seat_type_id, discount_id))
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Verknüpfung nicht gefunden'}), 404
                conn.commit()
                return jsonify({'message': 'Discount vom Sitztyp entfernt'}), 200
    except Exception as e:
        logger.error(f"Fehler beim Entfernen des Discounts vom Sitztyp: {e}")
        return jsonify({'error': 'Fehler beim Entfernen des Discounts vom Sitztyp'}), 500

@app.route('/seat_types_with_discounts', methods=['GET'])  #SucheDis
def get_seat_types_with_discounts():
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        st.seat_type_id,
                        st.name AS seat_type_name,
                        st.price, 
                        st.color,
                        st.icon,
                        d.discount_id,
                        d.name AS discount_name,
                        d.description,
                        std.discount_amount,
                        std.discount_percentage,
                        std.seat_type_discount_id
                    FROM seat_types st
                    LEFT JOIN seat_type_discounts std ON st.seat_type_id = std.seat_type_id
                    LEFT JOIN discounts d ON std.discount_id = d.discount_id
                    ORDER BY st.seat_type_id
                """)
                results = cursor.fetchall()

                seat_types = {}
                for row in results:
                    seat_type_id = row['seat_type_id']
                    if seat_type_id not in seat_types:
                        seat_types[seat_type_id] = {
                            'seat_type_id': seat_type_id,
                            'name': row['seat_type_name'],
                            'price': float(row['price']),
                            'color': row['color'],
                            'icon': row['icon'],
                            'discounts': []
                        }
                    if row['discount_id']:
                        seat_types[seat_type_id]['discounts'].append({
                            'discount_id': row['discount_id'],
                            'name': row['discount_name'],
                            'description': row['description'],
                            'discount_amount': float(row['discount_amount']) if row['discount_amount'] else None,
                            'discount_percentage': float(row['discount_percentage']) if row['discount_percentage'] else None,
                            'seat_type_discount_id': row['seat_type_discount_id']
                        })

                seat_types_list = list(seat_types.values())

        return jsonify({'seat_types': seat_types_list}), 200
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Sitztypen mit Discounts: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der Sitztypen mit Discounts'}), 500



@app.route('/discount/<int:seat_type_id>', methods=['GET']) 
def get_discount_for_seat_type(seat_type_id):
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        std.discount_id,
                        std.seat_type_discount_id,
                        d.name AS discount_name,
                        d.description,
                        std.discount_amount,
                        std.discount_percentage
                    FROM seat_type_discounts std
                    JOIN discounts d ON std.discount_id = d.discount_id
                    WHERE std.seat_type_id = %s
                """, (seat_type_id,))
                results = cursor.fetchall()

                discounts = []
                for row in results:
                    discounts.append({
                        'discount_id': row['discount_id'],
                        'seat_type_discount_id': row['seat_type_discount_id'],
                        'name': row['discount_name'],
                        'description': row['description'],
                        'discount_amount': float(row['discount_amount']) if row['discount_amount'] else None,
                        'discount_percentage': float(row['discount_percentage']) if row['discount_percentage'] else None
                    })

        return jsonify({'discounts': discounts}), 200
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Discounts für Sitztyp: {e}")
        return jsonify({'error': 'Fehler beim Abrufen des Discounts für Sitztyp'}), 500




@app.route('/movie/<int:movie_id>/trailer_url', methods=['GET'])
def get_movie_trailer_url(movie_id):
    # URL für die TMDB-API mit der spezifischen Film-ID
    url = f"{TMDB_API_URL}/{movie_id}/videos?language=de-DE"

    # Anfrage an die API senden
    response = requests.get(url, headers=HEADERS)
    
    # Erfolgreiche Antwort zurückgeben
    if response.status_code == 200:
        data = response.json()
        
        # Filtert den Eintrag mit 'type' == 'Trailer' und 'site' == 'YouTube'
        trailer = next((item for item in data.get('results', []) if item.get('type') == 'Trailer' and item.get('site') == 'YouTube'), None)
        
        if trailer and 'key' in trailer:
            embed_url = f"https://www.youtube.com/embed/{trailer['key']}"
            return jsonify({"trailer_url": embed_url}), 200
        else:
            return jsonify({"error": "No Trailer found."}), 404
    else:
        return jsonify({"error": f"Unable to fetch Trailer for movie ID {movie_id}"}), response.status_code
    

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
                        'price': float(bs['price']),
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
                'total_amount': float(booking['total_amount']),
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



@app.route('/user/points', methods=['GET'])
@token_required
def get_user_points():
    user_id = request.user.get('user_id')
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT points FROM user_points WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                if result:
                    return jsonify({'points': result[0]}), 200
                else:
                    return jsonify({'points': 0}), 200
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Punkte: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der Punkte'}), 500


@app.route('/user/points/redeem', methods=['POST'])
@token_required
def redeem_points():
    user_id = request.user.get('user_id')
    data = request.get_json()
    points_to_redeem = data.get('points')
    reward_id = data.get('reward_id')  # Neuen Parameter hinzufügen

    # Validierung der Eingabedaten
    if not points_to_redeem or not isinstance(points_to_redeem, int) or points_to_redeem <= 0:
        return jsonify({'error': 'Ungültige Punkteanzahl'}), 400

    if not reward_id or not isinstance(reward_id, int):
        return jsonify({'error': 'Ungültige reward_id'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                # Beginne eine Transaktion
                cursor.execute("BEGIN;")

                # Überprüfen, ob die Belohnung existiert und die erforderlichen Punkte stimmt
                cursor.execute("SELECT points FROM rewards WHERE reward_id = %s", (reward_id,))
                reward = cursor.fetchone()
                if not reward:
                    conn.rollback()
                    return jsonify({'error': 'Belohnung nicht gefunden'}), 404

                required_points = reward[0]
                if points_to_redeem != required_points:
                    conn.rollback()
                    return jsonify({'error': 'Die Anzahl der einzulösenden Punkte stimmt nicht mit der Belohnung überein'}), 400

                # Überprüfen, ob der Benutzer genügend Punkte hat
                cursor.execute("SELECT points FROM user_points WHERE user_id = %s FOR UPDATE", (user_id,))
                result = cursor.fetchone()
                if not result or result[0] < points_to_redeem:
                    conn.rollback()
                    return jsonify({'error': 'Nicht genügend Punkte'}), 400

                # Punkte abziehen
                cursor.execute("""
                    UPDATE user_points
                    SET points = points - %s,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                """, (points_to_redeem, user_id))

                # Transaktion protokollieren mit reward_id
                cursor.execute("""
                    INSERT INTO points_transactions (user_id, points_change, description, reward_id)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, -points_to_redeem, 'Einlösung von Punkten für Belohnung', reward_id))

                # Transaktion committen
                conn.commit()

        return jsonify({'message': f'{points_to_redeem} Punkte erfolgreich für die Belohnung eingelöst'}), 200

    except Exception as e:
        logger.error(f"Fehler beim Einlösen der Punkte: {e}")
        return jsonify({'error': 'Fehler beim Einlösen der Punkte'}), 500


@app.route('/user/points/transactions', methods=['GET'])
@token_required
def get_points_transactions():
    user_id = request.user.get('user_id')
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("""
                    SELECT pt.transaction_id, pt.points_change, pt.description, pt.timestamp, pt.reward_id, r.title AS reward_title, r.points AS reward_points, r.image AS reward_image, r.description AS reward_description
                    FROM points_transactions pt
                    JOIN rewards r ON pt.reward_id = r.reward_id
                    WHERE user_id = %s
                    ORDER BY timestamp DESC
                """, (user_id,))
                transactions = cursor.fetchall()
                transactions_list = [
                    {
                        'transaction_id': t['transaction_id'],
                        'points_change': t['points_change'],
                        'description': t['description'],
                        'timestamp': t['timestamp'].isoformat(),
                        'reward': {
                            'reward_id': t['reward_id'],
                            'title': t['reward_title'],
                            'points': t['reward_points'],
                            'image': t['reward_image'],
                            'description': t['reward_description']
                        }

                    }
                    for t in transactions
                ]
        return jsonify({'transactions': transactions_list}), 200
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Punkte-Transaktionen: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der Punkte-Transaktionen'}), 500
    


@app.route('/rewards', methods=['GET'])
def get_rewards():
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT reward_id, title, points, description, image FROM rewards")
                rewards = cursor.fetchall()
                rewards_list = [dict(r) for r in rewards]
        return jsonify({'rewards': rewards_list}), 200
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Belohnungen: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der Belohnungen'}), 500
    
@app.route('/rewards', methods=['POST'])
@admin_required
def add_reward():
    data = request.get_json()
    title = data.get('title')
    points = data.get('points')
    description = data.get('description', '')
    image = data.get('image', '')

    if not title or not points:
        return jsonify({'error': 'Titel und Punkte sind erforderlich'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO rewards (title, points, description, image)
                    VALUES (%s, %s, %s, %s)
                """, (title, points, description, image))
                conn.commit()
                return jsonify({'message': 'Belohnung hinzugefügt'}), 201
    except Exception as e:
        logger.error(f"Fehler beim Hinzufügen der Belohnung: {e}")
        return jsonify({'error': 'Fehler beim Hinzufügen der Belohnung'}), 500
    
@app.route('/rewards/<int:reward_id>', methods=['PUT'])
@admin_required
def update_reward(reward_id):
    data = request.get_json()
    title = data.get('title')
    points = data.get('points')
    description = data.get('description', '')
    image = data.get('image', '')

    if not title or not points:
        return jsonify({'error': 'Titel und Punkte sind erforderlich'}), 400

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE rewards
                    SET title = %s,
                        points = %s,
                        description = %s,
                        image = %s
                    WHERE reward_id = %s
                """, (title, points, description, image, reward_id))
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Belohnung nicht gefunden'}), 404
                conn.commit()
                return jsonify({'message': 'Belohnung aktualisiert'}), 200
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren der Belohnung: {e}")
        return jsonify({'error': 'Fehler beim Aktualisieren der Belohnung'}), 500
    

@app.route('/rewards/<int:reward_id>', methods=['DELETE'])
@admin_required
def delete_reward(reward_id):
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM rewards WHERE reward_id = %s", (reward_id,))
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Belohnung nicht gefunden'}), 404
                conn.commit()
                return jsonify({'message': 'Belohnung gelöscht'}), 200
    except Exception as e:
        logger.error(f"Fehler beim Löschen der Belohnung: {e}")
        return jsonify({'error': 'Fehler beim Löschen der Belohnung'}), 500

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("""
                    SELECT up.user_id, u.nickname, up.points, u.profile_image, COUNT(b.booking_id) AS bookings, MAX(s.start_time) AS last_booking, SUM(EXTRACT(EPOCH FROM (s.end_time - s.start_time)) / 60) AS total_duration
                    FROM users u
                    JOIN user_points up ON u.id = up.user_id
                    LEFT JOIN bookings b ON u.id = b.user_id
                    JOIN booking_seats bs ON b.booking_id = bs.booking_id
                    JOIN showtimes s ON bs.showtime_id = s.showtime_id
                    GROUP BY up.user_id, u.nickname, up.points, u.profile_image
                    ORDER BY  total_duration DESC
                    
                """)
                users = cursor.fetchall()
                users_list = [dict(u) for u in users]
        return jsonify({'leaderboard': users_list}), 200
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Leaderboards: {e}")
        return jsonify({'error': 'Fehler beim Abrufen des Leaderboards'}), 500
    

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


#-->Um den Sitzen im Warenkorb einen Discount (ermäßigung) zu geben
@app.route('/user/cart/update', methods=['POST'])
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
        with psycopg2.connect(DATABASE_URL) as conn:
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
    


@app.route('/guest/cart/update', methods=['POST'])
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
        with psycopg2.connect(DATABASE_URL) as conn:
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


#############################################################################################################
###################################     Hier Supermarktkasse    #############################################
#############################################################################################################

@app.route('/supermarkt/items', methods=['GET'])
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



if __name__ == '__main__':
    app.run(debug=True)
