import re

from docker.errors import DockerException, NotFound, APIError
from fastapi import HTTPException


def decode_mixed_bytestream(bytestream):
    result = []
    i = 0
    length = len(bytestream)

    def decode_utf8_segment(start, end):
        return bytestream[start:end].decode('utf-8')

    def decode_utf16_segment(start, end):
        return bytestream[start:end].encode('utf-16')

    while i < length:
        if i + 1 < length and bytestream[i:i+2] in [b'\xff\xfe', b'\xfe\xff']:
            bom = bytestream[i:i+2]
            j = i + 2
            while j < length - 1:
                if bytestream[j:j+2] in [b'\xff\xfe', b'\xfe\xff']:
                    break
                j += 2

            result.append(decode_utf16_segment(i, j))
            i = j
        else:
            j = i
            while j < length:
                if j + 1 < length and bytestream[j:j + 2] in [b'\xff\xfe', b'\xfe\xff']:
                    break;
                j += 1

            result.append(decode_utf8_segment(i, j))
            i = j

    return ''.join(result)


def handle_docker_exception(e: DockerException):
    if isinstance(e, NotFound):
        raise HTTPException(status_code=404, detail=str(e))
    elif isinstance(e, APIError):
        raise HTTPException(status_code=e.status_code, detail=str(e))
    else:
        raise HTTPException(status_code=500, detail="Docker error: " + str(e))


def parse_list_response(response):
    try:
        pattern = 'There are (\\d+) of a max of (\\d+) players online'
        match = re.search(pattern, response)

        if match:
            current_players = int(match.group(1))
            max_players = int(match.group(2))
        else:
            current_players = -1
            max_players = -1

        player_list = response.split(':')[1].strip().split(', ')

        return {'current_players': current_players, 'max_players': max_players, 'players_list': player_list}

    except Exception as e:
        print(f"Error parsing player list: {e}")
        return None

