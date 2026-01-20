# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_cors import CORS
import os

from .config import Config

# ============================
# Extensions
# ============================
db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")

# ============================
# Factory
# ============================
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)

    # Register blueprints
    from routes.accounts import auth_bp
    from routes.users import users_bp
    from routes.chats import chats_bp
    from routes.messages import messages_bp
    from routes.status import status_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(chats_bp, url_prefix="/chats")
    app.register_blueprint(messages_bp)
    app.register_blueprint(status_bp, url_prefix="/status")

    # Create tables
    with app.app_context():
        db.create_all()

    return app

# ============================
# Run with SocketIO
# ============================
app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)