from datetime import datetime, timedelta
import pytest
from unittest import mock

from sportblurbs.league import League, nfl

league_name = "SLN"
season_start = (6, 1)
season_start_dt = datetime(2021, season_start[0], season_start[1])
current_year = datetime.utcnow().year
season_year = current_year if datetime.utcnow() < season_start_dt else current_year - 1
player_id = "TestPlayerId"


@pytest.fixture
def league():
    return League(
        name=league_name,
        league_module=mock.MagicMock(),
        season_start=season_start,
    )


def test_get_current_season(league):
    assert league.get_season() == season_year


@pytest.mark.parametrize(
    "date,multiyear,expected_season",
    [
        (season_start_dt, False, 2021),
        (season_start_dt - timedelta(days=1), False, 2020),
        (season_start_dt, True, "2021-22"),
        (season_start_dt - timedelta(days=1), True, "2020-21"),
    ],
)
def test_get_season_for_a_given_date(league, date, multiyear, expected_season):
    league.multiyear = multiyear
    assert league.get_season(date) == expected_season


def test_get_player_from_the_current_season(league):
    league.get_player(player_id)
    assert league.league_module.roster.Player.call_args[0][0] == player_id
    assert league.league_module.roster.Player(player_id).call_args[0][0] == str(season_year)


@pytest.mark.parametrize("season", [2021, "2021-22"])
def test_get_player_from_a_given_season(league, season):
    league.get_player(player_id, season)
    assert league.league_module.roster.Player.call_args[0][0] == player_id
    assert league.league_module.roster.Player(player_id).call_args[0][0] == str(season)


@pytest.mark.parametrize(
    "date,expected_week",
    [
        (datetime(year=2014, month=8, day=5), (2014, "preseason")),
        (datetime(year=2014, month=9, day=2), (2014, 1)),
        (datetime(year=2014, month=12, day=28), (2014, 17)),
        (datetime(year=2014, month=12, day=30), (2014, "postseason")),
        (datetime(year=2022, month=1, day=9), (2021, 18)),
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
