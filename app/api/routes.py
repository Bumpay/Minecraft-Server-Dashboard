from docker.errors import NotFound, DockerException
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from . import api

from dotenv import load_dotenv
import os
import docker

from .rcon import send_rcon_command
from .utils import parse_list_response

load_dotenv()

docker_client = docker.DockerClient(base_url=f'tcp://{os.getenv("SERVER_HOST")}:{os.getenv("DOCKER_DAEMON_PORT")}')

# Example user database
users = {
    os.getenv('ADMIN_USERNAME'): os.getenv('ADMIN_PASSWORD')
}


@api.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
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


@api.route('/rcon/command', methods=['POST'])
@jwt_required()
def rcon_command():
    data = request.get_json()
    command = data.get('command')
    response = send_rcon_command(command)
    return jsonify({"response": response})


@api.route('/server/resources', methods=['GET'])
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

        used_memory = stats['memory_stats']['usage']    # - stats['memory_stats']['stats']['cache'] # Cache field is missing although API states it exists: https://docs.docker.com/engine/api/v1.45/#tag/Container/operation/ContainerStats
        print(stats['memory_stats']['stats'])
        available_memory = stats['memory_stats']['limit']
        memory_usage_percent = (used_memory / available_memory) * 100

        return jsonify({
            "cpu_usage": f"{cpu_usage_percent:.2f} %",
            "memory_usage": f"{round(used_memory / (1024 * 1024 * 1024), 2)} GB",
            "memory_limit": f"{round(available_memory / (1024 * 1024 * 1024), 2)} GB",
            "memory_percent": f"{round(memory_usage_percent, 2)} %"
        })

    except NotFound as e:
        return jsonify({"message": f"Container '{container_name}' not found: {str(e)}"}), 404

    except DockerException as e:
        return jsonify({"message": f"Docker error: {str(e)}"}), 500


@api.route('/logs', methods=['GET'])
@jwt_required()
def fetch_logs():
    logs = [
        "[INFO] Server started.",   # TODO: Dummy
        "[INFO] Player joined."
    ]
    return jsonify({"logs": logs})
