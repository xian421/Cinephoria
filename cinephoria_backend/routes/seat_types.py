# cinephoria_backend/routes/seat_types.py

from flask import Blueprint, jsonify, request
from cinephoria_backend.config import DATABASE_URL, get_db_connection
from cinephoria_backend.routes.auth import admin_required

seat_types_bp = Blueprint('seat_types', __name__)


@seat_types_bp.route('/seat_types', methods=['GET'])
def get_seat_types():
    try:
        with get_db_connection() as conn:
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


@seat_types_bp.route('/seat_types', methods=['POST'])
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
        with get_db_connection() as conn:
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


@seat_types_bp.route('/seat_types/<int:seat_type_id>', methods=['PUT'])
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
        with get_db_connection() as conn:
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

@seat_types_bp.route('/seat_types/<int:seat_type_id>', methods=['DELETE'])
@admin_required
def delete_seat_type(seat_type_id):
    try:
        with get_db_connection() as conn:
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
