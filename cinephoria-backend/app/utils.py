import os
import psycopg2
from flask import request, jsonify
import jwt
from functools import wraps
from datetime import datetime, timedelta, timezone
from .config import Config

def get_db_connection():
    return psycopg2.connect(Config.DATABASE_URL)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token fehlt'}), 401
        try:
            decoded = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            request.user = decoded
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token abgelaufen'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Ungültiges Token'}), 401
        return f(*args, **kwargs)
    return decorated
