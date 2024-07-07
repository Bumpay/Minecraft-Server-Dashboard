import asyncio
import json
import os
from typing import List
from asyncio import sleep

import docker
from docker.errors import NotFound, DockerException
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from backend.rcon import send_rcon_command
from backend.utils import decode_mixed_bytestream, handle_docker_exception, parse_list_response

app = FastAPI()

load_dotenv()

client = docker.DockerClient(base_url=f'tcp://{os.getenv("SERVER_HOST")}:{os.getenv("DOCKER_DAEMON_PORT")}')


@app.get("/servers", response_model=List[str])
async def get_servers():
    try:
        server_list = []
        containers = client.containers.list()

        for container in containers:
            server_list.append(container.name)

        return server_list
    except DockerException as e:
        handle_docker_exception(e)


@app.get("/servers/{server_id}")
async def get_server(server_id: str):
    raise NotImplementedError


@app.post("/servers/{server_id}/start")
async def start_server(server_id: str, response: Response):
    try:
        container = client.containers.get(server_id)

        print(container)
        if container.status == "running":
            response.status_code = 304
            return
        else:
            container.start()
            response.status_code = 204
            return

    except DockerException as e:
        handle_docker_exception(e)


@app.post("/servers/{server_id}/stop")
async def stop_server(server_id: str, response: Response):
    try:
        container = client.containers.get(server_id)

        if container.status == "stopped":
            response.status_code = 304
            return
        else:
            container.stop()
            response.status_code = 204
            return

    except DockerException as e:
        handle_docker_exception(e)


@app.post("/servers/{server_id}/restart")
async def restart_server(server_id: str, response: Response):
    try:
        container = client.containers.get(server_id)

        container.restart()
        response.status_code = 204
        return

    except DockerException as e:
        handle_docker_exception(e)


@app.get("/servers/{server_id}/status")
async def server_status(server_id: str, response: Response):
    try:
        container = client.containers.get(server_id)

        status = container.status
        return {"status": status}

    except DockerException as e:
        handle_docker_exception(e)


@app.get("/servers/{server_id}/players")
async def get_players(server_id: str):
    try:
        container = client.containers.get(server_id)

        response_players = send_rcon_command('list')
        players_info = parse_list_response(response_players)
        return {"players": players_info["players_list"], "max_players": players_info["max_players"]}

    except DockerException as e:
        handle_docker_exception(e)


@app.put("/servers/{server_id}/config")
async def update_config(server_id: str):
    raise NotImplementedError


@app.post("/servers/{server_id}/command")
async def send_command(server_id: str):
    raise NotImplementedError


@app.get("/servers/{server_id}/metrics")
async def stream_server_metrics(server_id: str):
    return StreamingResponse(get_container_metrics(server_id), media_type="text/event-stream")


async def get_container_metrics(server_id: str):
    try:
        container = client.containers.get(server_id)
        if container.attrs['State']['Status'] == 'exited':
            raise HTTPException(status_code=500, detail="Container exited")

        while True:
            stats = container.stats(stream=False)

            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
            system_cpu_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            number_cpus = stats['cpu_stats']['online_cpus']
            cpu_usage_percent = (cpu_delta / system_cpu_delta) * number_cpus * 100.0

            # Cache field is missing although API states it exists: https://docs.docker.com/engine/api/v1.45/#tag/Container/operation/ContainerStats
            used_memory = stats['memory_stats']['usage'] - stats['memory_stats']['stats']['inactive_file']
            available_memory = stats['memory_stats']['limit']
            memory_usage_percent = (used_memory / available_memory) * 100

            metrics = {
                "cpu_usage": f"{cpu_usage_percent:.2f} %",
                "memory_usage": f"{round(used_memory / (1024 * 1024 * 1024), 2)} GB",
                "memory_limit": f"{round(available_memory / (1024 * 1024 * 1024), 2)} GB",
                "memory_percent": f"{round(memory_usage_percent, 2)} %"
            }

            print(metrics)

            yield f'data: {json.dumps(metrics)}\n\n'

            await sleep(1)

    except docker.errors.NotFound as e:
        raise HTTPException(status_code=404, detail=f'Container \'{server_id}\' not found: {str(e)}')

    # except docker.errors.DockerException as e:
    #     return {"message": f"Docker error: {str(e)}"}, 500

    except Exception as e:
        error_str = str(e).replace('\n', ' ')
        yield f'data: An error occured: {error_str}\n\n'


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
