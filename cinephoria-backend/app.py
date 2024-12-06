# app.py

import os
import psycopg2
import psycopg2.extras
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import jwt
import datetime
from functools import wraps

app = Flask(__name__, static_folder='public', static_url_path='')

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


@app.route('/paypal/order/create', methods=['POST'])
@token_required
def create_paypal_order():
    data = request.get_json()
    showtime_id = data.get('showtime_id')
    selected_seats = data.get('selected_seats')  # Erwartet eine Liste von Sitzplatz-Dictionaries

    if not showtime_id or not selected_seats:
        return jsonify({'error': 'showtime_id und selected_seats sind erforderlich'}), 400

    try:
        token = get_paypal_access_token()

        seat_ids = [seat['seat_id'] for seat in selected_seats]

        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                # Preise und Details für die ausgewählten Sitzplätze abrufen
                cursor.execute("""
                    SELECT s.seat_id, s.row, s.number, st.name AS seat_type_name, st.price
                    FROM seats s
                    JOIN seat_types st ON s.seat_type_id = st.seat_type_id
                    WHERE s.seat_id = ANY(%s)
                """, (seat_ids,))
                seats_data = cursor.fetchall()
                if not seats_data:
                    return jsonify({'error': 'Keine gültigen Sitzplätze gefunden'}), 400

                items = []
                total_amount = 0.0
                for seat in seats_data:
                    seat_id, row, number, seat_type_name, price = seat
                    total_amount += float(price)
                    items.append({
                        "name": f"Reihe {row} Sitz {number} ({seat_type_name})",
                        "quantity": "1",
                        "unit_amount": {
                            "currency_code": "EUR",
                            "value": f"{float(price):.2f}"
                        }
                    })

        order_payload = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": "EUR",
                    "value": f"{total_amount:.2f}",
                    "breakdown": {
                        "item_total": {
                            "currency_code": "EUR",
                            "value": f"{total_amount:.2f}"
                        }
                    }
                },
                "items": items
            }],
            "application_context": {
                "return_url": "https://cinephoria-theta.vercel.app/upcoming",
                "cancel_url": "https://cinephoria-theta.vercel.app/nowplaying"
            }
        }

        response = requests.post(
            f"{PAYPAL_API_BASE}/v2/checkout/orders",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            json=order_payload
        )

        if response.status_code == 201:
            order = response.json()
            return jsonify({'orderID': order['id']}), 201
        else:
            print(f"PayPal Order Creation Failed: {response.status_code}")
            print(response.json())
            return jsonify({'error': 'Fehler beim Erstellen der PayPal-Order', 'details': response.json()}), 500

    except Exception as e:
        print(f"Fehler beim Erstellen der PayPal-Order: {e}")
        return jsonify({'error': 'Fehler beim Erstellen der PayPal-Order'}), 500


@app.route('/paypal/order/capture', methods=['POST'])
@token_required  # Optional: Nur authentifizierte Benutzer können Orders erfassen
def capture_paypal_order():
    data = request.get_json()
    order_id = data.get('orderID')

    if not order_id:
        return jsonify({'error': 'orderID ist erforderlich'}), 400

    try:
        token = get_paypal_access_token()

        response = requests.post(
            f"{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )

        if response.status_code == 201:
            capture = response.json()
            return jsonify({'status': capture['status']}), 201
        else:
            print(response.json())
            return jsonify({'error': 'Fehler beim Erfassen der PayPal-Order'}), 500

    except Exception as e:
        print(f"Fehler beim Erfassen der PayPal-Order: {e}")
        return jsonify({'error': 'Fehler beim Erfassen der PayPal-Order'}), 500

# PayPal Ende

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
                        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
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

    if not vorname and not nachname and not email and not password:
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
                    SELECT showtime_id, movie_id, screen_id, start_time, end_time
                    FROM showtimes
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
                    'end_time': row[4].isoformat() if row[4] else None
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

@app.route('/bookings', methods=['POST'])
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
                    WHERE b.showtime_id = %s AND b.payment_status = 'completed' AND bs.seat_id = ANY(%s)
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
                
                # Commit der Transaktion
                conn.commit()
        
        return jsonify({'message': 'Buchung erfolgreich', 'booking_id': booking_id}), 201
    except Exception as e:
        print(f"Fehler beim Erstellen der Buchung: {e}")
        return jsonify({'error': 'Fehler beim Erstellen der Buchung'}), 500

@app.route('/showtimes/<int:showtime_id>/seats', methods=['GET'])
@token_required  # Optional: Falls nur authentifizierte Benutzer Sitzplätze abrufen dürfen
def get_seats_for_showtime(showtime_id):
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                # Ermitteln des Kinosaals für die Showtime
                cursor.execute("""
                    SELECT screen_id FROM showtimes WHERE showtime_id = %s
                """, (showtime_id,))
                screen = cursor.fetchone()
                if not screen:
                    return jsonify({'error': 'Showtime nicht gefunden'}), 404
                screen_id = screen[0]
                
                # Abrufen aller Sitzplätze für den Kinosaal
                cursor.execute("""
                    SELECT s.seat_id, s.row, s.number, st.name AS seat_type_name, st.price, st.color, st.icon
                    FROM seats s
                    JOIN seat_types st ON s.seat_type_id = st.seat_type_id
                    WHERE s.screen_id = %s
                    ORDER BY s.row, s.number
                """, (screen_id,))
                seats = cursor.fetchall()
                
                # Abrufen aller bereits gebuchten Sitzplätze für die Showtime
                cursor.execute("""
                    SELECT bs.seat_id FROM booking_seats bs
                    JOIN bookings b ON bs.booking_id = b.booking_id
                    WHERE b.showtime_id = %s AND b.payment_status = 'completed'
                """, (showtime_id,))
                booked_seat_ids = {row[0] for row in cursor.fetchall()}
                
                # Strukturieren der Sitzplatzdaten
                seats_list = []
                for seat in seats:
                    seat_id, row, number, seat_type_name, price, color, icon = seat
                    status = 'unavailable' if seat_id in booked_seat_ids else 'available'
                    seats_list.append({
                        'seat_id': seat_id,
                        'row': row,
                        'number': number,
                        'type': seat_type_name,
                        'price': float(price),
                        'color': color or '#678be0',
                        'icon': icon,
                        'status': status
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

@app.route('/profile', methods=['GET'])
@token_required
def profile():
    user_id = request.user.get('user_id')
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT vorname, nachname, email, role, profile_image FROM users WHERE id = %s", (user_id,))
                result = cursor.fetchone()
                if not result:
                    return jsonify({'error': 'Benutzer nicht gefunden'}), 404
                vorname, nachname, email, role, profile_image = result
                return jsonify({
                    'vorname': vorname,
                    'nachname': nachname,
                    'email': email,
                    'role': role,
                    'profile_image': profile_image
                }), 200
    except Exception as e:
        print(f"Fehler beim Abrufen des Profils: {e}")
        return jsonify({'error': 'Fehler beim Abrufen des Profils'}), 500

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


if __name__ == '__main__':
    app.run(debug=True)
