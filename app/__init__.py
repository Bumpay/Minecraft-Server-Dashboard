from flask import Flask
from flask_jwt_extended import JWTManager


def create_app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # TODO: change key

    jwt = JWTManager(app)

    with app.app_context():
        from . import routes
        app.register_blueprint(routes.bp)

    return app
