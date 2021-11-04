import logging

logger = logging.getLogger()


def player_is_home(player, boxscore):
    return player.team_abbreviation.upper() == boxscore.home_abbreviation.upper()


def game_is_complete(boxscore):
    return boxscore.home_points is not None
