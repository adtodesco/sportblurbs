from dateutil import parser
import logging
import openai

from .utils import game_score, player_is_home

logger = logging.getLogger()


def write_generic_player_news(boxscore, player, player_boxscore):
    day_of_week = parser.parse(boxscore.date).strftime("%A")
    away_score, home_score = game_score(boxscore)
    return (
        f"{player.name} played in the {boxscore.winning_name}'s {home_score} - {away_score} win over the "
        f"{boxscore.losing_name} on {day_of_week}."
    )


def _stat_summary(stats, include_zeros=False):
    summary = list()
    for stat in stats:
        if stat[0] == 1:
            summary.append(f"a {stat[1]}")
        elif stat[0] != 0 or include_zeros:
            summary.append(f"{stat[0]} {stat[1]}s")

    if not summary:
        return ""
    elif len(summary) == 1:
        return summary[0]
    else:
        return ", ".join(summary[:-1]) + " and " + summary[-1]


def _nfl_passing_stat_summary(player_boxscore, include_zeros=False):
    return _stat_summary(
        [
            (player_boxscore.passing_yards, "yard"),
            (player_boxscore.passing_touchdowns, "touchdown"),
            (player_boxscore.interceptions, "interception"),
        ],
        include_zeros=include_zeros,
    )


def _nfl_rushing_stat_summary(player_boxscore, include_zeros=False):
    return _stat_summary(
        [
            (player_boxscore.rush_yards, "yard"),
            (player_boxscore.rush_touchdowns, "touchdown"),
            (player_boxscore.fumbles_lost, "fumble"),
        ],
        include_zeros=include_zeros,
    )


def _nfl_receiving_stat_summary(player_boxscore, include_zeros=False):
    return _stat_summary(
        [
            (player_boxscore.receiving_yards, "yard"),
            (player_boxscore.recieving_touchdowns, "touchdown"),
            (player_boxscore.fumbles_lost, "fumble"),
        ],
        include_zeros=include_zeros,
    )


def write_nfl_player_news(boxscore, player, player_boxscore):
    day_of_week = parser.parse(boxscore.date).strftime("%A")
    away_score, home_score = game_score(boxscore)
    news = list()
    if player.position == "QB":
        news.append(
            f"{player.name} completed {player_boxscore.completed_passes} of {player_boxscore.attempted_passes} pass "
            f"attempts for"
        )
        news.append(_nfl_passing_stat_summary(player_boxscore))
        if player_boxscore.rush_attempts > 0:
            news.append(f"while rushing {player_boxscore.rush_attempts} times for")
            news.append(_nfl_rushing_stat_summary(player_boxscore))
    elif player.position == "RB":
        news.append(f"{player.name} rushed {player_boxscore.rush_attempts} times for")
        news.append(_nfl_rushing_stat_summary(player_boxscore))
        if player_boxscore.receptions > 0:
            news.append(f"while catching {player_boxscore.receptions} of {player_boxscore.targets} targets for")
            news.append(_nfl_receiving_stat_summary(player_boxscore))
    elif player.position in ["WR", "TE"]:
        news.append(f"{player.name} caught {player_boxscore.receptions} of {player_boxscore.targets} targets for")
        news.append(_nfl_receiving_stat_summary(player_boxscore))
        if player_boxscore.rush_attempts > 0:
            news.append(f"while rushing {player_boxscore.rush_attempts} times for")
            news.append(_nfl_rushing_stat_summary(player_boxscore))
    elif player.position == "K":
        news.append(f"{player.name}")
        if player_boxscore.field_goals_attempted > 0:
            news.append(
                f"made {player_boxscore.field_goals_made} of {player_boxscore.field_goals_attempted} field goals"
            )
            if player_boxscore.extra_points_attempted > 0:
                news.append(
                    f"while going {player_boxscore.extra_points_made} for {player_boxscore.extra_points_attempted} on "
                    f"PATs"
                )
        elif player_boxscore.extra_points_attempted > 0:
            news.append(
                f"went {player_boxscore.extra_points_made} for {player_boxscore.extra_points_attempted} on PATs"
            )
        else:
            news.append("did not appear")
    else:
        news.append(f"{player.name} played")

    news.append(f"in {day_of_week}'s {away_score}-{home_score}")
    is_home = player_is_home(player, boxscore)
    if (is_home and home_score > away_score) or (not is_home and home_score < away_score):
        news.append(f"win over the {boxscore.losing_name}.")
    else:
        news.append(f"loss to the {boxscore.winning_name}.")

    return " ".join(news)


def write_null_spin(news):
    return ""


def write_player_blurbs_from_boxscore(
    boxscore,
    league,
    news_func=write_generic_player_news,
    spin_func=write_null_spin,
    filters=None,
):
    if callable(filters):
        filters = [filters]
    blurbs = list()
    for player_boxscore in boxscore.home_players + boxscore.away_players:
        player = league.get_player(player_boxscore.player_id)
        if filters and not all(func(boxscore, player, player_boxscore) for func in filters):
            logging.debug(f"filtering out {player.name}")
            continue
        logging.debug(f"writing blurb for {player.name}")
        news = news_func(boxscore, player, player_boxscore)
        spin = spin_func(news)
        blurbs.append({"player": player, "news": news, "spin": spin})

    return blurbs
