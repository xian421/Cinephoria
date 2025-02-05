from flask import Blueprint, request, jsonify, current_app as app
import jwt
from datetime import datetime, timedelta, timezone
import psycopg2
from .config import Config
from .utils import get_db_connection, token_required  # Falls du diese Funktionen in utils.py auslagerst

DATABASE_URL = Config.DATABASE_URL

discounts_bp = Blueprint('discounts', __name__)

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
        return jsonify({'error': 'Fehler beim Abrufen der Discounts'}), 500