from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os


def create_app():
    app = Flask(__name__)

    # Load environment variables
    load_dotenv()

    # Configure JWT
    secret_key = os.getenv('SECRET_KEY')
    jwt_secret_key = os.getenv('JWT_SECRET_KEY')
    app.config['SECRET_KEY'] = secret_key
    app.config['JWT_SECRET_KEY'] = jwt_secret_key
    jwt = JWTManager(app)

    # Register Blueprints
    from .dashboard import dashboard as dashboard_blueprint
    from .api import api as api_blueprint

    app.register_blueprint(dashboard_blueprint)
    app.register_blueprint(api_blueprint, url_prefix='/api')

    print(f"Current template folder: {app.template_folder}")

    return app
