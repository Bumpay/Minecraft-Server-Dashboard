import re


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
