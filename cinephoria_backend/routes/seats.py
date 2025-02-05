# cinephoria_backend/routes/seats.py
from flask import Blueprint, jsonify, request
from cinephoria_backend.config import get_db_connection
import psycopg2.extras
from cinephoria_backend.routes.auth import admin_required

seats_bp = Blueprint('seats', __name__)




@seats_bp.route('/seats', methods=['POST'])
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
        with get_db_connection() as conn:
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

@seats_bp.route('/seats/<int:seat_id>', methods=['DELETE'])
@admin_required
def delete_seat(seat_id):
    try:
        with get_db_connection() as conn:
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

@seats_bp.route('/seats', methods=['DELETE'])
@admin_required
def delete_all_seats():
    screen_id = request.args.get('screen_id')
    if not screen_id:
        return jsonify({'error': 'Screen ID ist erforderlich'}), 400

    try:
        with get_db_connection() as conn:
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

@seats_bp.route('/seats', methods=['GET'])
def get_seats():
    screen_id = request.args.get('screen_id')
    if not screen_id:
        return jsonify({'error': 'screen_id ist erforderlich'}), 400

    try:
        with get_db_connection() as conn:
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


@seats_bp.route('/seats/<seat_id>', methods=['GET'])
def get_seat(seat_id):
    try:
        with get_db_connection() as conn:
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


@seats_bp.route('/seats/batch_update', methods=['POST'])
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
        with get_db_connection() as conn:
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
