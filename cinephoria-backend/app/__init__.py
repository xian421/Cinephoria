from flask import Flask
from flask_cors import CORS
import logging
from .config import Config

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../public', static_url_path='')
    app.config.from_object(config_class)

    # Logging konfigurieren
    logging.basicConfig(level=logging.INFO)

    # CORS konfigurieren (Passe dies ggf. an)
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

    # Blueprints importieren und registrieren
    from .auth import auth_bp
    from .movies import movies_bp
    from .bookings import bookings_bp
    from .supermarkt import supermarkt_bp
    from .discounts import discounts_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(movies_bp, url_prefix='/movies')
    app.register_blueprint(bookings_bp, url_prefix='/bookings')
    app.register_blueprint(supermarkt_bp, url_prefix='/supermarkt')
    app.register_blueprint(discounts_bp, url_prefix='/discounts')

    return app
