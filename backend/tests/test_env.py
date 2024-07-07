import os
from dotenv import load_dotenv
import pytest


load_dotenv()


def test_env_variables():
    rcon_host = os.getenv('RCON_HOST')
    rcon_port = os.getenv('RCON_PORT')
    rcon_pass = os.getenv('RCON_PASSWORD')

    assert rcon_host is not None, "RCON_HOST should not be None"
    assert rcon_port is not None, "RCON_PORT should not be None"
    assert rcon_pass is not None, "RCON_PASSWORD should not be None"

    assert rcon_pass == 'rcon_password', "RCON_PASSWORD should be 'rcon_password'"
    assert rcon_host == '192.168.2.50', "RCON_HOST should be 'localhost'"
    assert rcon_port == '25575', "RCON_PORT should be '25575'"


if __name__ == '__main__':
    pytest.main()
