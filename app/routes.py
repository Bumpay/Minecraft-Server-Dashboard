from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required
from dotenv import load_dotenv
import os
import docker
from .rcon import send_rcon_command
from .utils import parse_list_response
from docker.errors import DockerException, NotFound
import time


load_dotenv()

# Example user database
users = {
    os.getenv('ADMIN_USERNAME'): os.getenv('ADMIN_PASSWORD')
}

bp = Blueprint('main', __name__)

docker_client = docker.DockerClient(base_url=f'tcp://{os.getenv("SERVER_HOST")}:{os.getenv("DOCKER_DAEMON_PORT")}')


@bp.route('/index')
def index():
    return render_template('index.html')

previous_stats = {}

@bp.route('/server/resources', methods=['GET'])
@jwt_required()
def server_resources():
    container_name = os.getenv('CONTAINER_NAME')

    try:
        container = docker_client.containers.get(container_name)
        stats = container.stats(stream=False)

        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
        system_cpu_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
        number_cpus = stats['cpu_stats']['online_cpus']
        cpu_usage_percent = (cpu_delta / system_cpu_delta) * number_cpus * 100.0

        memory_usage = stats['memory_stats']['usage']
        memory_limit = stats['memory_stats']['limit']
        memory_percent = (memory_usage / memory_limit) * 100

        return jsonify({
            "cpu_usage": f"{cpu_usage_percent:.2f} %",
            "memory_usage": f"{round(memory_usage / (1024 * 1024 * 1024), 2)} GB",
            "memory_limit": f"{round(memory_limit / (1024 * 1024 * 1024), 2)} GB",
            "memory_percent": f"{round(memory_percent, 2)} %"
        })

    except NotFound as e:
        return jsonify({"message": f"Container '{container_name}' not found: {str(e)}"}), 404

    except DockerException as e:
        return jsonify({"message": f"Docker error: {str(e)}"}), 500


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
