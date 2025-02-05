# cinephoria_backend/routes/discounts.py
from flask import Blueprint, jsonify, request
import psycopg2.extras
from cinephoria_backend.config import get_db_connection
from cinephoria_backend.routes.auth import admin_required

discounts_bp = Blueprint('discounts', __name__)


@discounts_bp.route('/discounts', methods=['GET'])
def get_discounts():
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT discount_id, name, description FROM discounts")
                discounts = cursor.fetchall()
                discounts_list = [dict(d) for d in discounts]
        return jsonify({'discounts': discounts_list}), 200
    except Exception as e:
        return jsonify({'error': 'Fehler beim Abrufen der Discounts'}), 500

    

@discounts_bp.route('/discounts', methods=['POST'])
@admin_required
def add_discount():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')

    if not name:
        return jsonify({'error': 'Name ist erforderlich'}), 400

    try:
        with get_db_connection() as conn:
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
        return jsonify({'error': 'Fehler beim Hinzufügen des Discounts'}), 500
    
        
@discounts_bp.route('/discounts/<int:discount_id>', methods=['PUT'])
@admin_required
def update_discount(discount_id):
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')

    if not name:
        return jsonify({'error': 'Name ist erforderlich'}), 400

    try:
        with get_db_connection() as conn:
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
        return jsonify({'error': 'Fehler beim Aktualisieren des Discounts'}), 500
    

@discounts_bp.route('/discounts/<int:discount_id>', methods=['DELETE'])
@admin_required
def delete_discount(discount_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM discounts WHERE discount_id = %s", (discount_id,))
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Discount nicht gefunden'}), 404
                conn.commit()
                return jsonify({'message': 'Discount gelöscht'}), 200
    except Exception as e:
        return jsonify({'error': 'Fehler beim Löschen des Discounts'}), 500
    

@discounts_bp.route('/seat_type_discounts', methods=['POST'])
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
        with get_db_connection() as conn:
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
        return jsonify({'error': 'Fehler beim Zuweisen des Discounts zu Sitztyp'}), 500


@discounts_bp.route('/seat_type_discounts', methods=['DELETE'])
@admin_required
def remove_discount_from_seat_type():
    data = request.get_json()
    seat_type_id = data.get('seat_type_id')
    discount_id = data.get('discount_id')

    if not seat_type_id or not discount_id:
        return jsonify({'error': 'seat_type_id und discount_id sind erforderlich'}), 400

    try:
        with get_db_connection() as conn:
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
        return jsonify({'error': 'Fehler beim Entfernen des Discounts vom Sitztyp'}), 500

@discounts_bp.route('/seat_types_with_discounts', methods=['GET'])  #SucheDis
def get_seat_types_with_discounts():
    try:
        with get_db_connection() as conn:
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
        return jsonify({'error': 'Fehler beim Abrufen der Sitztypen mit Discounts'}), 500



@discounts_bp.route('/discount/<int:seat_type_id>', methods=['GET']) 
def get_discount_for_seat_type(seat_type_id):
    try:
        with get_db_connection() as conn:
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
        return jsonify({'error': 'Fehler beim Abrufen des Discounts für Sitztyp'}), 500


