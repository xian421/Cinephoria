# cinephoria_backend/routes/showtimes.py
from flask import Blueprint, jsonify, request
import jwt
from psycopg2.extras import DictCursor
from cinephoria_backend.config import get_db_connection, SECRET_KEY
from cinephoria_backend.routes.auth import admin_required

showtimes_bp = Blueprint('showtimes', __name__)


@showtimes_bp.route('/showtimes', methods=['POST'])
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
        with get_db_connection() as conn:
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

@showtimes_bp.route('/showtimes', methods=['GET'])
def get_showtimes():
    screen_id = request.args.get('screen_id')  # Optional: Filter nach Screen
    movie_id = request.args.get('movie_id')    # Optional: Filter nach Movie
    try:
        with get_db_connection() as conn:
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
    
  
@showtimes_bp.route('/showtimes/aktuell', methods=['GET'])
def get_showtimes_today():
    movie_id = request.args.get('movie_id')  # Optionaler Parameter
    try:
        with get_db_connection() as conn:
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

    


@showtimes_bp.route('/showtimes/<int:showtime_id>', methods=['PUT'])
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
        with get_db_connection() as conn:
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
    

@showtimes_bp.route('/showtimes/<int:showtime_id>/seats', methods=['GET'])
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
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
           # cursor.execute("DELETE FROM guest_cart_items WHERE reserved_until < NOW()")
            #cursor.execute("DELETE FROM user_cart_items WHERE reserved_until < NOW()")
            print('Test')

    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
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


