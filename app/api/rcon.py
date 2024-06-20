import os
from mcrcon import MCRcon

RCON_HOST = os.getenv('RCON_HOST')
RCON_PORT = os.getenv('RCON_PORT')
RCON_PASSWORD = os.getenv('RCON_PASSWORD')


def send_rcon_command(command):
    with MCRcon(RCON_HOST, RCON_PASSWORD) as mcr:
        response = mcr.command(command)
    return response
