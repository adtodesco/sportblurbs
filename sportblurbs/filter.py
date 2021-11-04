import logging

logger = logging.getLogger()


def filter_player_has_position(boxscore, player, player_boxscore):
    try:
        return player.position
    except TypeError:
        logger.debug(f"player {player_boxscore.name}'s position attribute could not be checked.", exc_info=True)
        return False


def filter_player_has_team(boxscore, player, player_boxscore):
    try:
        return player.team_abbreviation
    except TypeError:
        logger.debug(
            f"player {player_boxscore.name}'s team_abbreviation attribute could not be checked.", exc_info=True
        )
        return False


def filter_nfl_at_least_one_att(boxscore, player, player_boxscore):
    try:
        return (
            player_boxscore.attempted_passes
            or player_boxscore.rush_attempts
            or player_boxscore.receptions
            or player_boxscore.field_goals_attempted
        )
    except TypeError:
        logger.debug(f"player {player_boxscore.name}'s boxscore attribute(s) could not be checked.", exc_info=True)
        return False


def filter_nba_at_least_one_minute_played(boxscore, player, player_boxscore):
    try:
        return player_boxscore.minutes_played
    except TypeError:
        logger.debug(f"player {player_boxscore.name}'s minutes_played attribute could not be checked.", exc_info=True)
        return False
