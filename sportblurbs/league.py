import datetime

import sportsipy.mlb
import sportsipy.mlb.boxscore
import sportsipy.mlb.roster

import sportsipy.nfl
import sportsipy.nfl.boxscore
import sportsipy.nfl.roster

import sportsipy.nba
import sportsipy.nba.boxscore
import sportsipy.nba.roster


class League:
    def __init__(self, name, league_module):
        self.name = name
        self.league_module = league_module
        self._boxscores = dict()

    def get_player(self, player_id, season=None):
        if not season:
            # TODO: Add per-league season methods (i.e. NBA is 2021-22, NFL is 2021 until Feb, etc.)
            season = datetime.datetime.utcnow().year
        return self.league_module.roster.Player(player_id)(str(season))

    def get_games(self, date):
        return self.league_module.boxscore.Boxscores(date).games[self.date_string(date)]

    def get_boxscores(self, date):
        date_string = self.date_string(date)
        if date_string not in self._boxscores:
            games = self.get_games(date)
            self._boxscores[date_string] = [self.league_module.boxscore.Boxscore(game["boxscore"]) for game in games]

        return self._boxscores[date_string]

    @staticmethod
    def date_string(date):
        return date.strftime("%m-%-d-%Y")


class NflLeague(League):
    def get_games(self, date):
        return self.league_module.boxscore.Boxscores(week=date[0], year=date[1]).games[self.date_string(date)]

    @staticmethod
    def date_string(date):
        return str(date[0]) + "-" + str(date[1])


MLB = League("MLB", sportsipy.mlb)
NFL = NflLeague("NFL", sportsipy.nfl)
NBA = League("NBA", sportsipy.nba)
