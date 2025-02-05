from flask import Blueprint, request, jsonify
import jwt
from datetime import datetime, timedelta, timezone
import psycopg2
from .config import Config
from .utils import get_db_connection, token_required  # Falls du diese Funktionen in utils.py auslagerst

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'E-Mail und Passwort sind erforderlich'}), 400

    try:
        conn = get_db_connection()
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
                }, Config.SECRET_KEY, algorithm='HS256')
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
