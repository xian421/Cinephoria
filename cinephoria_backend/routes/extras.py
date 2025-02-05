# cinephoria_backend/routes/extras.py
from flask import Blueprint, jsonify, request
import psycopg2
import psycopg2.extras
from cinephoria_backend.config import get_db_connection
from cinephoria_backend.routes.auth import token_required, admin_required
from cinephoria_backend.config import TMDB_API_URL, HEADERS
import requests


extras_bp = Blueprint('extras', __name__)


@extras_bp.route('/bookings', methods=['GET'])
@token_required
def get_user_bookings():
    user_id = request.user.get('user_id')
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:

                # Abfrage: Buchungsdaten inkl. aggregierter Sitzplätze
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
                        sc.name AS screen_name,
                        json_agg(
                            json_build_object(
                                'seat_id', bs.seat_id,
                                'price', COALESCE(bs.price, 0)::numeric,
                                'row', s2.row,
                                'number', s2.number,
                                'seat_type', st.name,
                                'seat_type_discount_id', bs.seat_type_discount_id
                            )
                        ) AS seats
                    FROM bookings b
                    JOIN booking_seats bs ON b.booking_id = bs.booking_id
                    JOIN showtimes s ON bs.showtime_id = s.showtime_id
                    JOIN screens sc ON s.screen_id = sc.screen_id
                    JOIN seats s2 ON bs.seat_id = s2.seat_id
                    JOIN seat_types st ON s2.seat_type_id = st.seat_type_id
                    WHERE b.user_id = %s
                    GROUP BY 
                        b.booking_id, bs.showtime_id, b.total_amount, b.payment_status, 
                        b.paypal_order_id, b.created_at, s.movie_id, s.screen_id, 
                        s.start_time, s.end_time, sc.name
                    ORDER BY b.created_at DESC
                """, (user_id,))
                bookings = cursor.fetchall()

                if not bookings:
                    return jsonify({'bookings': []}), 200

                # Sammeln aller eindeutigen movie_ids, um später die Filmdetails abzurufen
                movie_ids = list({booking['movie_id'] for booking in bookings})

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
                'seats': booking['seats']  # bereits als JSON aggregiert
            }
            bookings_list.append(booking_dict)

        return jsonify({'bookings': bookings_list}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': 'Fehler beim Abrufen der Buchungen'}), 500




@extras_bp.route('/user/points', methods=['GET'])
@token_required
def get_user_points():
    user_id = request.user.get('user_id')
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT points FROM user_points WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                if result:
                    return jsonify({'points': result[0]}), 200
                else:
                    return jsonify({'points': 0}), 200
    except Exception as e:
        return jsonify({'error': 'Fehler beim Abrufen der Punkte'}), 500


@extras_bp.route('/user/points/redeem', methods=['POST'])
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
        with get_db_connection() as conn:
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
        return jsonify({'error': 'Fehler beim Einlösen der Punkte'}), 500


@extras_bp.route('/user/points/transactions', methods=['GET'])
@token_required
def get_points_transactions():
    user_id = request.user.get('user_id')
    try:
        with get_db_connection() as conn:
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
        return jsonify({'error': 'Fehler beim Abrufen der Punkte-Transaktionen'}), 500
    


@extras_bp.route('/rewards', methods=['GET'])
def get_rewards():
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT reward_id, title, points, description, image FROM rewards")
                rewards = cursor.fetchall()
                rewards_list = [dict(r) for r in rewards]
        return jsonify({'rewards': rewards_list}), 200
    except Exception as e:
        return jsonify({'error': 'Fehler beim Abrufen der Belohnungen'}), 500
    
@extras_bp.route('/rewards', methods=['POST'])
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
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO rewards (title, points, description, image)
                    VALUES (%s, %s, %s, %s)
                """, (title, points, description, image))
                conn.commit()
                return jsonify({'message': 'Belohnung hinzugefügt'}), 201
    except Exception as e:
        return jsonify({'error': 'Fehler beim Hinzufügen der Belohnung'}), 500
    
@extras_bp.route('/rewards/<int:reward_id>', methods=['PUT'])
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
        with get_db_connection() as conn:
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
        return jsonify({'error': 'Fehler beim Aktualisieren der Belohnung'}), 500
    

@extras_bp.route('/rewards/<int:reward_id>', methods=['DELETE'])
@admin_required
def delete_reward(reward_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM rewards WHERE reward_id = %s", (reward_id,))
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Belohnung nicht gefunden'}), 404
                conn.commit()
                return jsonify({'message': 'Belohnung gelöscht'}), 200
    except Exception as e:
        return jsonify({'error': 'Fehler beim Löschen der Belohnung'}), 500

@extras_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        with get_db_connection() as conn:
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
        return jsonify({'error': 'Fehler beim Abrufen des Leaderboards'}), 500
    

