from datetime import datetime, timedelta
import pytest
from unittest import mock

from sportblurbs.league import League, nfl

test_league_name = "SLN"
test_season_start = (6, 1)
test_season_start_dt = datetime(2020, test_season_start[0], test_season_start[1])
test_player_id = "TestPlayerId"


@pytest.fixture
def test_league():
    return League(
        name=test_league_name,
        league_module=mock.MagicMock(),
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
def test_get_season_for_a_given_date(test_league, date, multiyear, expected_season):
    test_league.multiyear = multiyear
    assert test_league.get_season(date) == expected_season


def test_get_player_from_the_current_season(test_league):
    test_league.get_player(test_player_id)
    assert test_league.league_module.roster.Player.call_args[0][0] == test_player_id
    assert test_league.league_module.roster.Player(test_player_id).call_args[0][0] == str(datetime.utcnow().year)


@pytest.mark.parametrize("season", [2021, "2021-22"])
def test_get_player_from_a_given_season(test_league, season):
    test_league.get_player(test_player_id, season)
    assert test_league.league_module.roster.Player.call_args[0][0] == test_player_id
    assert test_league.league_module.roster.Player(test_player_id).call_args[0][0] == str(season)


@pytest.mark.parametrize(
    "date,expected_week",
    [
        (datetime(year=2014, month=8, day=5), (2014, "preseason")),
        (datetime(year=2014, month=9, day=2), (2014, 1)),
        (datetime(year=2014, month=12, day=28), (2014, 17)),
        (datetime(year=2014, month=12, day=30), (2014, "postseason")),
        (datetime(year=2021, month=1, day=9), (2021, 18)),
    ],
)
def test_nfl_get_week_for_a_given_date(date, expected_week):
    assert nfl.get_week(date) == expected_week


@pytest.mark.parametrize(
    "start_date,end_date,expected_weeks",
    [
        (datetime(year=2014, month=8, day=5), datetime(year=2014, month=8, day=15), list()),
        (datetime(year=2014, month=8, day=5), datetime(year=2014, month=10, day=5), [(2014, w) for w in range(1, 6)]),
        (
            datetime(year=2014, month=8, day=1),
            datetime(year=2016, month=2, day=10),
            [(y, w) for y in range(2014, 2016) for w in range(1, 18)],
        ),
    ],
)
def test_nfl_get_weeks_between_a_date_range(start_date, end_date, expected_weeks):
    assert nfl.get_weeks(start_date, end_date) == expected_weeks
