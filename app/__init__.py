from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os


def create_app():
    app = Flask(__name__)
    load_dotenv()

    rcon_password = os.getenv('RCON_PASSWORD')
    jwt_secret_key = os.getenv('JWT_SECRET_KEY')

    app.config['JWT_SECRET_KEY'] = jwt_secret_key

    jwt = JWTManager(app)

    with app.app_context():
        from . import routes
        app.register_blueprint(routes.bp)

    return app
