from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app, supports_credentials=True,
         origins=["http://localhost:8000", "http://127.0.0.1:8000"])

    from routes.auth import auth_bp
    from routes.menu import menu_bp
    from routes.cart import cart_bp
    from routes.orders import orders_bp
    from routes.payments import payments_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp,     url_prefix='/api/auth')
    app.register_blueprint(menu_bp,     url_prefix='/api/menu')
    app.register_blueprint(cart_bp,     url_prefix='/api/cart')
    app.register_blueprint(orders_bp,   url_prefix='/api/orders')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(admin_bp,    url_prefix='/api/admin')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
