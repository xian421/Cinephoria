# cinephoria_backend/routes/auth.py

from flask import Blueprint, request, jsonify, current_app
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
import os

# Importiere die zentralen Konfigurationswerte aus config.py
from cinephoria_backend.config import DATABASE_URL, SECRET_KEY, get_db_connection

# Erstelle den Blueprint
auth_bp = Blueprint('auth', __name__)

# Middleware für Token-Validierung
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token fehlt'}), 401
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = decoded  # Speichere die Nutzerdaten in request.user
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token abgelaufen'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Ungültiges Token'}), 401
        return f(*args, **kwargs)
    return decorated

def token_optional(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return None
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = decoded  # Speichere die Nutzerdaten in request.user
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
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

# Token Validierung Endpunkt
@auth_bp.route('/validate-token', methods=['POST'])
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

# Login-Endpunkt
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'E-Mail und Passwort sind erforderlich'}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, password, vorname, nachname, role FROM users WHERE email = %s",
                    (email,)
                )
                result = cursor.fetchone()
                if not result:
                    return jsonify({'error': 'Ungültige E-Mail oder Passwort'}), 401

                user_id, stored_password, vorname, nachname, role = result

                # Passwortüberprüfung (mithilfe der PostgreSQL crypt()-Funktion)
                cursor.execute(
                    "SELECT crypt(%s, %s) = %s AS password_match",
                    (password, stored_password, stored_password)
                )
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

# Registrierungs-Endpunkt
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    vorname = data.get('first_name')
    nachname = data.get('last_name')
    email = data.get('email')
    password = data.get('password')

    if not vorname or not nachname or not email or not password:
        return jsonify({'error': 'Alle Felder sind erforderlich'}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Prüfen, ob der Benutzer bereits existiert
                cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    return jsonify({'error': 'Benutzer mit dieser E-Mail existiert bereits'}), 409

                # Passwort hashen mit der PostgreSQL crypt()-Funktion
                cursor.execute(
                    "INSERT INTO users (vorname, nachname, email, password) VALUES (%s, %s, %s, crypt(%s, gen_salt('bf')))",
                    (vorname, nachname, email, password)
                )
        return jsonify({'message': 'Registrierung erfolgreich'}), 201

    except Exception as e:
        print(f"Fehler bei der Registrierung: {e}")
        return jsonify({'error': 'Fehler bei der Registrierung'}), 500

# Profil-Endpunkt (GET und PUT)
@auth_bp.route('/profile', methods=['GET', 'PUT'])
@token_required
def profile():
    user_id = request.user.get('user_id')

    if request.method == 'GET':
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT vorname, nachname, email, role, profile_image, nickname 
                        FROM users 
                        WHERE id = %s
                    """, (user_id,))
                    result = cursor.fetchone()
                    if not result:
                        return jsonify({'error': 'Benutzer nicht gefunden'}), 404
                    vorname, nachname, email, role, profile_image, nickname = result
                    return jsonify({
                        'vorname': vorname,
                        'nachname': nachname,
                        'email': email,
                        'role': role,
                        'profile_image': profile_image,
                        'nickname': nickname
                    }), 200
        except Exception as e:
            print(f"Fehler beim Abrufen des Profils: {e}")
            return jsonify({'error': 'Fehler beim Abrufen des Profils'}), 500

    elif request.method == 'PUT':
        data = request.get_json()
        vorname = data.get('vorname')
        nachname = data.get('nachname')
        email = data.get('email')
        nickname = data.get('nickname')
        role = data.get('role')

        if not vorname or not nachname or not email:
            return jsonify({'error': 'Alle Felder sind erforderlich'}), 400

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE users 
                        SET vorname = %s, nachname = %s, email = %s, nickname = %s, role = %s
                        WHERE id = %s
                    """, (vorname, nachname, email, nickname, role, user_id))
                    conn.commit()
            return jsonify({'message': 'Profil aktualisiert'}), 200
        except Exception as e:
            print(f"Fehler beim Aktualisieren des Profils: {e}")
            return jsonify({'error': 'Fehler beim Aktualisieren des Profils'}), 500



def get_allowed_profile_images():
    # Nutze current_app.static_folder, falls du das in Blueprints oder in App-Kontexten verwenden möchtest
    profile_images_dir = os.path.join(current_app.static_folder, 'Profilbilder')
    try:
        images = [f for f in os.listdir(profile_images_dir) if os.path.isfile(os.path.join(profile_images_dir, f))]
        return images
    except Exception as e:
        current_app.logger.error(f"Fehler beim Abrufen der Profilbilder: {e}")
        return []




# Neuer Endpunkt zum Aktualisieren des Profilbildes
@auth_bp.route('/profile/image', methods=['PUT'])
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
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE users SET profile_image = %s WHERE id = %s", (profile_image, user_id))
                conn.commit()
        return jsonify({'message': 'Profilbild aktualisiert'}), 200
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Profilbildes: {e}")
        return jsonify({'error': 'Fehler beim Aktualisieren des Profilbildes'}), 500

# Neuer Endpunkt zum Auflisten der verfügbaren Profilbilder
@auth_bp.route('/profile/images', methods=['GET'])
@token_required
def list_profile_images():
    try:
        images = get_allowed_profile_images()
        return jsonify({'images': images}), 200
    except Exception as e:
        print(f"Fehler beim Auflisten der Profilbilder: {e}")
        return jsonify({'error': 'Fehler beim Auflisten der Profilbilder'}), 500
    
