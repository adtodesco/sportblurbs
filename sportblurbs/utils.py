from .exception import KeyNotFoundError


def player_is_home(player, boxscore):
    return player.team_abbreviation.upper() == boxscore.home_abbreviation.upper()


def game_is_complete(boxscore):
    return game_score(boxscore)[0] is not None


def game_score(boxscore):
    try:
        return boxscore.home_points, boxscore.away_points
    except AttributeError:
        return boxscore.home_runs, boxscore.away_runs


def get_value_from_document(key, document):
    value = document
    for key_part in key.split("."):
        try:
            value = value[key_part]
        except KeyError:
            raise KeyNotFoundError(key, document)

    return value
