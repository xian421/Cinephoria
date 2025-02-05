# app.py
from flask import Flask


from cinephoria_backend.routes.movies import movies_bp
from cinephoria_backend.routes.screens import screens_bp
from cinephoria_backend.routes.auth import auth_bp
from cinephoria_backend.routes.paypal import paypal_bp
from cinephoria_backend.routes.seats import seats_bp
from cinephoria_backend.routes.seat_types import seat_types_bp
from cinephoria_backend.routes.showtimes import showtimes_bp
from cinephoria_backend.routes.usercart import user_cart_bp
from cinephoria_backend.routes.guestcart import guest_cart_bp
from cinephoria_backend.routes.supermarkt import supermarkt_bp
from cinephoria_backend.routes.discounts import discounts_bp
from cinephoria_backend.routes.extras import extras_bp
from cinephoria_backend.routes.qr import qr_bp



app = Flask(__name__, static_folder='public', static_url_path='')


# Einzelne Module verwenden
app.register_blueprint(movies_bp, url_prefix='')
app.register_blueprint(screens_bp, url_prefix='')
app.register_blueprint(auth_bp, url_prefix='')
app.register_blueprint(paypal_bp, url_prefix='')
app.register_blueprint(seats_bp, url_prefix='')
app.register_blueprint(seat_types_bp, url_prefix='')
app.register_blueprint(showtimes_bp, url_prefix='')
app.register_blueprint(user_cart_bp, url_prefix='')
app.register_blueprint(guest_cart_bp, url_prefix='')
app.register_blueprint(supermarkt_bp, url_prefix='')
app.register_blueprint(discounts_bp, url_prefix='')
app.register_blueprint(extras_bp, url_prefix='')
app.register_blueprint(qr_bp, url_prefix='')



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



if __name__ == '__main__':
    app.run(debug=True)