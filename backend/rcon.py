import os
from mcrcon import MCRcon


def send_rcon_command(command):
    rcon_host = os.getenv('RCON_HOST')
    rcon_port = os.getenv('RCON_PORT')
    rcon_password = os.getenv('RCON_PASSWORD')

    print(f"RCON Debug: RCON Host: {rcon_host}, RCON Port: {rcon_port}")
    with MCRcon(rcon_host, rcon_password) as mcr:
        response = mcr.command(command)
    return response
