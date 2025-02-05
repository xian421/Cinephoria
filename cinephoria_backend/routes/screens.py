# cinephoria_backend/routes/screens.py

from flask import Blueprint, jsonify, request
from cinephoria_backend.config import get_db_connection

screens_bp = Blueprint('screens', __name__)


@screens_bp.route('/cinemas', methods=['GET'])
def get_cinemas():
    try:
        with get_db_connection() as conn:
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

@screens_bp.route('/screens', methods=['GET'])
def get_screens():
    cinema_id = request.args.get('cinema_id', default=1, type=int)  # Standardwert: 1
    try:
        with get_db_connection() as conn:
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

