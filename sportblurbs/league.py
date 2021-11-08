from datetime import datetime, timedelta

import sportsipy.mlb
import sportsipy.mlb.boxscore
import sportsipy.mlb.roster

import sportsipy.nfl
import sportsipy.nfl.boxscore
import sportsipy.nfl.roster
from sportsipy.nfl.schedule import Schedule

import sportsipy.nba
import sportsipy.nba.boxscore
import sportsipy.nba.roster


class League:
    def __init__(self, name, league_module, season_start, multiyear=False):
        self.name = name
        self.league_module = league_module
        self.season_start = season_start
        self.multiyear = multiyear
        self._boxscores = dict()

    def get_season(self, date=datetime.utcnow()):
        if date < datetime(year=date.year, month=self.season_start[0], day=self.season_start[1]):
            season = date.year - 1
        else:
            season = date.year
        if self.multiyear:
            season = f"{season}-{int(season[2:]) + 1}"
        return season

    def get_player(self, player_id, season=None):
        if not season:
            season = self.get_season()
        return self.league_module.roster.Player(player_id)(str(season))

    def get_games(self, date=datetime.utcnow()):
        return self.league_module.boxscore.Boxscores(date).games[self.date_string(date)]

    def get_boxscores(self, date=datetime.utcnow()):
        date_string = self.date_string(date)
        if date_string not in self._boxscores:
            games = self.get_games(date)
            self._boxscores[date_string] = [self.league_module.boxscore.Boxscore(game["boxscore"]) for game in games]
        return self._boxscores[date_string]

    @staticmethod
    def date_string(date):
        return date.strftime("%m-%-d-%Y")


class NflLeague(League):
    def __init__(self, name, league_module, season_start, multiyear=False):
        self._schedule = dict()
        super().__init__(name, league_module, season_start, multiyear)

    def _build_schedule(self, season):
        # Here we're just using the sportsipy team Schedule class to get a generic NFL season schedule.  Any team would
        # work, but the Pats work the best.
        # TODO: Handle building when season does not exist (too old or in future)
        patriots_schedule = Schedule("NWE", season)
        season_schedule = list()
        for game_dt in patriots_schedule.dataframe["datetime"]:
            game_week_dt = game_dt - timedelta(days=1)
            season_schedule.append(game_week_dt - timedelta(days=game_week_dt.weekday() - 1))

        self._schedule[season] = season_schedule

    def get_games(self, date=datetime.utcnow()):
        if isinstance(date, datetime):
            date = self.get_week(date)

        return self.league_module.boxscore.Boxscores(week=date[0], year=date[1]).games[self.date_string(date)]

    def get_week(self, date=datetime.utcnow()):
        # TODO: Extend to include preseason and postseason weeks
        season = self.get_season(date)
        if season not in self._schedule:
            self._build_schedule(season)

        week = "preseason"
        week_num, week_dt = None, None
        for week_num, week_dt in enumerate(self._schedule[season], start=1):
            if date < week_dt:
                return season, week
            else:
                week = week_num

        if date < (week_dt + timedelta(days=7)):
            return season, week_num + 1

        return season, "postseason"

    def get_weeks(self, start_date, end_date):
        start_season, start_week = self.get_week(start_date)
        end_season, end_week = self.get_week(end_date)

        if start_week == "preseason":
            start_week = 1
        if start_week == "postseason":
            start_season = int(start_season) + 1
            start_week = 1
        if end_week == "preseason":
            season_length = 17 if int(end_season - 1) >= 2021 else 16
            end_season = int(end_season) - 1
            end_week = season_length
        if end_week == "postseason":
            season_length = 17 if int(end_season) >= 2021 else 16
            end_week = season_length

        weeks = [(start_season, start_week)]
        temp_season, temp_week = start_season, start_week
        while temp_season < end_season or (temp_season == end_season and temp_week <= end_week):
            weeks.append((temp_season, temp_week))
            season_length = 17 if int(temp_season) >= 2021 else 16
            if int(temp_week) < season_length:
                temp_week = int(temp_week) + 1
            else:
                temp_season = int(temp_season) + 1
                temp_week = 1

        return weeks

    @staticmethod
    def date_string(date):
        return str(date[0]) + "-" + str(date[1])


mlb = League("MLB", sportsipy.mlb, season_start=(3, 15))
nfl = NflLeague("NFL", sportsipy.nfl, season_start=(8, 1))
nba = League("NBA", sportsipy.nba, season_start=(9, 15), multiyear=True)
