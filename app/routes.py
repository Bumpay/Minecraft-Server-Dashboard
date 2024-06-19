from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required
from dotenv import load_dotenv
import os
from .rcon import send_rcon_command
from .utils import parse_list_response


load_dotenv()

# Example user database
users = {
    os.getenv('ADMIN_USERNAME'): os.getenv('ADMIN_PASSWORD')
}

bp = Blueprint('main', __name__)


@bp.route('/index')
def index():
    return render_template('index.html')


@bp.route('/status', methods=['GET'])
def server_status():
    try:
        response_players = send_rcon_command('list')
        players_info = parse_list_response(response_players)

        status = {
            "online": True,     # Assuming server is online if RCON commands succeed
            "current_players": players_info['current_players'],
            "max_players": players_info['max_players'],
            "players": players_info['players_list']
        }

        return jsonify(status)

    except Exception as e:
        # Handle exceptions (e.g., RCON connection failure)
        error_message = {"error": str(e)}
        return jsonify(error_message), 500


@bp.route('/rcon/command', methods=['POST'])
@jwt_required()
def rcon_command():
    data = request.get_json()
    command = data.get('command')
    response = send_rcon_command(command)
    return jsonify({"response": response})


@bp.route('/logs', methods=['GET'])
@jwt_required()
def fetch_logs():
    logs = [
        "[INFO] Server started.",   # TODO: Dummy
        "[INFO] Player joined."
    ]
    return jsonify({"logs": logs})


@bp.route('/auth/login', methods=['POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'Could not verify'}), 401

    if users.get(auth.username) == auth.password:
        access_token = create_access_token(identity={'username': auth.username})
        return jsonify({"token": access_token})
    return jsonify({"message": "Invalid credentials"}), 401
