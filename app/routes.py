from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from .rcon import send_rcon_command

bp = Blueprint('main', __name__)

@bp.route('/status', methods=['GET'])
def server_status():
    status = {
        "online": True,    # TODO: Implement logic to check server status
        "players": 5,
        "maxPlayers": 10
    }
    return jsonify(status)


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
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username == 'admin' and password == 'password':  # TODO: Dummy
        token = create_access_token(identity={'username': username})
        return jsonify({"token": token})
    return jsonify({"message": "Invalid credentials"}), 401
