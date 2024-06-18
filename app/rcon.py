from mcrcon import MCRcon


def send_rcon_command(command):
    with MCRcon("localhost", "your_rcon_password") as mcr:  # TODO: Dummy
        response = mcr.command(command)
    return response
