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
    pfand_id = data.get('pfand_id')  
    
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
    pfand_id = data.get('pfand_id')  

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




if __name__ == '__main__':
    app.run(debug=True)
