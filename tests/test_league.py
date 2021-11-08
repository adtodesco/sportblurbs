from datetime import datetime, timedelta
import pytest
from unittest import mock

from sportblurbs.league import League

test_league_name = "SLN"
test_season_start = (6, 1)
test_season_start_dt = datetime(2020, test_season_start[0], test_season_start[1])
test_player_id = "TestPlayerId"


@pytest.fixture
def test_league():
    return League(
        name=test_league_name,
        league_module=mock.Mock(),
        season_start=test_season_start,
    )


def test_get_current_season(test_league):
    assert test_league.get_season() == str(datetime.utcnow().year)


@pytest.mark.parametrize(
    "date,multiyear,expected_season",
    [
        (test_season_start_dt, False, "2021"),
        (test_season_start_dt - timedelta(days=1), False, "2020"),
        (test_season_start_dt, True, "2021-22"),
        (test_season_start_dt - timedelta(days=1), True, "2020-21"),
    ],
)
def test_get_season_for_given_date(test_league, date, multiyear, expected_season):
    test_league.multiyear = multiyear
    assert test_league.get_season(date) == expected_season


def test_get_player_from_current_season(test_league):
    test_league.get_player(test_player_id)
    assert test_league.league_module.roster.Player.call_args[0][0] == test_player_id
    assert test_league.league_module.roster.Player(test_player_id).call_args[0][0] == str(datetime.utcnow().year)


@pytest.mark.parametrize("season", [2021, "2021-22"])
def test_get_player_from_given_season(test_league, season):
    test_league.get_player(test_player_id, season)
    assert test_league.league_module.roster.Player.call_args[0][0] == test_player_id
    assert test_league.league_module.roster.Player(test_player_id).call_args[0][0] == str(season)
