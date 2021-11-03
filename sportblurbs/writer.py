from dateutil import parser
import logging

import openai

logger = logging.getLogger()


# TODO: Probably don't actually need classes for the writers, individual writer funcitons should do the trick I think
class SpinWriter:
    def write(self, news):
        raise NotImplementedError()


class NullSpinWriter(SpinWriter):
    def write(self, news):
        return ""


class Gpt3SpinWriter(SpinWriter):
    def __init__(self, api_key):
        self._api_key = api_key

    def write(self, news):
        return "news spin"


class PlayerNewsWriter:
    def write(self, boxscore, player, player_boxscore):
        raise NotImplementedError()


class BasicPlayerNewsWriter(PlayerNewsWriter):
    def write(self, boxscore, player, player_boxscore):
        day_of_week = parser.parse(boxscore.date).strftime("%A")
        return (
            f"{player.name} played in the {boxscore.winning_name}'s {boxscore.away_points} - {boxscore.home_points} win"
            f" over the {boxscore.losing_name} on {day_of_week}."
        )


class NflPlayerNewsWriter(PlayerNewsWriter):
    def write(self, boxscore, player, player_boxscore):
        return f"{player.name}"

    @staticmethod
    def player_summary(player, player_boxscore):
        if player.position == "QB":
            summary = (
                f'completed {player_boxscore["comp"]} of {player_boxscore["att"]} pass attempts '
                f'for {player_boxscore["pass_yards"]} yards, {player_boxscore["td"]} touchdowns '
                f'and {player_boxscore["int"]} interceptions'
            )
            if player_boxscore["carr"] > 0:
                summary += " while rushing {} times for {} yards".format(
                    player_boxscore["carr"], player_boxscore["rush_yards"]
                )
        elif player.position in ["RB", "WR", "TE"]:
            summary = "{} for {} with"
        elif player.position == "DST":
            summary = "{}"
        elif player.position == "K":
            summary = ""
        else:
            summary = ""

        return summary


def write_player_blurbs_from_day(
    date, league, news_writer=BasicPlayerNewsWriter(), spin_writer=NullSpinWriter(), filters=None
):
    blurbs = list()
    boxscores = league.get_boxscores(date)
    for boxscore in boxscores:
        blurbs.extend(write_player_blurbs_from_boxscore(boxscore, league, news_writer, spin_writer, filters))

    return blurbs


def write_player_blurbs_from_boxscore(
    boxscore,
    league,
    news_writer=BasicPlayerNewsWriter(),
    spin_writer=NullSpinWriter(),
    filters=None,
):
    if callable(filters):
        filters = [filters]
    blurbs = list()
    for player_boxscore in boxscore.home_players + boxscore.away_players:
        player = league.get_player(player_boxscore.player_id)
        if filters and not all(func(boxscore, player, player_boxscore) for func in filters):
            logging.debug("filtering out " + player.name)
            continue
        logging.debug("writing blurb for " + player.name)
        news = news_writer.write(boxscore, player, player_boxscore)
        spin = spin_writer.write(news)
        blurbs.append({"player": player, "news": news, "spin": spin})

    return blurbs
