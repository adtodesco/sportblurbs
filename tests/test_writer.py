import pytest
from unittest import mock

from sportblurbs.league import League
from sportblurbs.writer import (
    write_nfl_player_news,
    write_player_blurbs_from_boxscore,
    _nfl_passing_stat_summary,
    _nfl_receiving_stat_summary,
    _nfl_rushing_stat_summary,
    _stat_summary,
)

boxscore_date = "06/15/2008"
boxscore_winning_name = "Melonheads"
boxscore_losing_name = "Wombats"
boxscore_home_points = 7
boxscore_away_points = 4

player_name = "Pablo Sanchez"


@pytest.fixture
def boxscore():
    bs = mock.Mock()
    bs.date = boxscore_date
    bs.winning_name = boxscore_winning_name
    bs.losing_name = boxscore_losing_name
    bs.home_points = boxscore_home_points
    bs.away_points = boxscore_away_points
    return bs


@pytest.fixture
def player():
    p = mock.Mock()
    p.name = player_name
    return p


nfl_player_completed_passes = 20
nfl_player_attempted_passes = 35
nfl_player_passing_yards = 350
nfl_player_passing_touchdowns = 2
nfl_player_interceptions = 1
nfl_player_fumbles_lost = 0
nfl_player_rush_attempts = 15
nfl_player_rush_yards = 100
nfl_player_rush_touchdowns = 1
nfl_player_receptions = 5
nfl_player_targets = 6
nfl_player_receiving_yards = 120
nfl_player_receiving_touchdowns = 1
nfl_player_field_goals_attempted = 2
nfl_player_field_goals_made = 1
nfl_player_extra_points_attempted = 2
nfl_player_extra_points_made = 2


@pytest.fixture
def nfl_player_boxscore():
    bs = mock.Mock()
    bs.completed_passes = nfl_player_completed_passes
    bs.attempted_passes = nfl_player_attempted_passes
    bs.passing_yards = nfl_player_passing_yards
    bs.passing_touchdowns = nfl_player_passing_touchdowns
    bs.interceptions = nfl_player_interceptions
    bs.fumbles_lost = nfl_player_fumbles_lost
    bs.rush_attempts = nfl_player_rush_attempts
    bs.rush_yards = nfl_player_rush_yards
    bs.rush_touchdowns = nfl_player_rush_touchdowns
    bs.targets = nfl_player_receptions
    bs.receptions = nfl_player_receptions
    bs.receiving_yards = nfl_player_receiving_yards
    bs.receiving_touchdowns = nfl_player_receiving_touchdowns
    bs.field_goals_attempted = nfl_player_attempted_passes
    bs.field_goals_made = nfl_player_attempted_passes
    bs.extra_points_attempted = nfl_player_attempted_passes
    bs.extra_points_made = nfl_player_attempted_passes
    return bs


league_name = "SLN"
season_start = (6, 1)
player_id = "TestPlayerId"


@pytest.fixture
def league():
    return League(
        name=league_name,
        league_module=mock.MagicMock(),
        season_start=season_start,
    )


@pytest.mark.parametrize(
    "stats,include_zeros,expected_summary",
    [
        ([], False, ""),
        ([(0, "touchdown")], False, ""),
        ([(1, "touchdown")], False, "a touchdown"),
        ([(100, "yard")], False, "100 yards"),
        ([(1, "touchdown"), (100, "yard")], False, "a touchdown and 100 yards"),
        ([(1, "touchdown"), (100, "yard"), (0, "interception")], False, "a touchdown and 100 yards"),
        ([(1, "touchdown"), (100, "yard"), (0, "interception")], True, "a touchdown, 100 yards and 0 interceptions"),
    ],
)
def test_stat_summary_returns_expected_summary(stats, include_zeros, expected_summary):
    assert _stat_summary(stats, include_zeros) == expected_summary


@pytest.mark.parametrize(
    "stats",
    [
        {
            "completed_passes": 20,
            "attempted_passes": 35,
            "passing_yards": 300,
            "passing_touchdowns": 2,
            "interceptions": 0,
            "fumbles_lost": 0,
            "rush_attempts": 0,
            "rush_touchdowns": 0,
            "rush_yards": 0,
        },
        {
            "completed_passes": 15,
            "attempted_passes": 25,
            "passing_yards": 150,
            "passing_touchdowns": 0,
            "interceptions": 1,
            "fumbles_lost": 1,
            "rush_attempts": 5,
            "rush_touchdowns": 0,
            "rush_yards": 10,
        },
    ],
)
def test_write_nfl_player_news_for_qbs(boxscore, player, nfl_player_boxscore, stats):
    player.position = "QB"
    nfl_player_boxscore.configure_mock(**stats)
    news = write_nfl_player_news(boxscore, player, nfl_player_boxscore)
    assert (
        f"{player_name} completed {nfl_player_boxscore.completed_passes} of {nfl_player_boxscore.attempted_passes}"
        in news
    )
    assert _nfl_passing_stat_summary(nfl_player_boxscore) in news
    if nfl_player_boxscore.rush_attempts > 0:
        assert f"while rushing {nfl_player_boxscore.rush_attempts} times" in news
        assert _nfl_rushing_stat_summary(nfl_player_boxscore) in news
    else:
        assert f"rush" not in news


@pytest.mark.parametrize(
    "stats",
    [
        {
            "fumbles_lost": 0,
            "rush_attempts": 15,
            "rush_touchdowns": 1,
            "rush_yards": 95,
        },
        {
            "fumbles_lost": 1,
            "rush_attempts": 12,
            "rush_touchdowns": 0,
            "rush_yards": 55,
            "targets": 3,
            "receptions": 2,
            "receiving_yards": 25,
            "receiving_touchdowns": 0,
        },
    ],
)
def test_write_nfl_player_news_for_rbs(boxscore, player, nfl_player_boxscore, stats):
    player.position = "RB"
    nfl_player_boxscore.configure_mock(**stats)
    news = write_nfl_player_news(boxscore, player, nfl_player_boxscore)
    assert f"{player_name} rushed {nfl_player_boxscore.rush_attempts} times" in news
    assert _nfl_rushing_stat_summary(nfl_player_boxscore) in news
    if nfl_player_boxscore.receptions > 0:
        assert f"while catching {nfl_player_boxscore.receptions} of {nfl_player_boxscore.targets} targets" in news
        assert _nfl_receiving_stat_summary(nfl_player_boxscore) in news
    else:
        assert f"catching" not in news


@pytest.mark.parametrize(
    "stats",
    [
        {
            "targets": 10,
            "receptions": 8,
            "receiving_yards": 150,
            "receiving_touchdowns": 2,
        },
        {
            "targets": 5,
            "receptions": 3,
            "receiving_yards": 31,
            "receiving_touchdowns": 0,
            "fumbles_lost": 1,
            "rush_attempts": 2,
            "rush_touchdowns": 0,
            "rush_yards": 10,
        },
    ],
)
def test_write_nfl_player_news_for_wrs(boxscore, player, nfl_player_boxscore, stats):
    player.position = "WR"
    nfl_player_boxscore.configure_mock(**stats)
    news = write_nfl_player_news(boxscore, player, nfl_player_boxscore)
    assert f"{player_name} caught {nfl_player_boxscore.receptions} of {nfl_player_boxscore.targets} target" in news
    assert _nfl_receiving_stat_summary(nfl_player_boxscore) in news
    if nfl_player_boxscore.rush_attempts > 0:
        assert f"while rushing {nfl_player_boxscore.rush_attempts} times" in news
        assert _nfl_rushing_stat_summary(nfl_player_boxscore) in news
    else:
        assert f"rush" not in news


@pytest.mark.parametrize(
    "stats",
    [
        {
            "targets": 10,
            "receptions": 8,
            "receiving_yards": 150,
            "receiving_touchdowns": 2,
        },
        {
            "targets": 5,
            "receptions": 3,
            "receiving_yards": 31,
            "receiving_touchdowns": 0,
            "fumbles_lost": 1,
            "rush_attempts": 2,
            "rush_touchdowns": 0,
            "rush_yards": 10,
        },
    ],
)
def test_write_nfl_player_news_for_tes(boxscore, player, nfl_player_boxscore, stats):
    player.position = "TE"
    nfl_player_boxscore.configure_mock(**stats)
    news = write_nfl_player_news(boxscore, player, nfl_player_boxscore)
    assert f"{player_name} caught {nfl_player_boxscore.receptions} of {nfl_player_boxscore.targets} target" in news
    assert _nfl_receiving_stat_summary(nfl_player_boxscore) in news
    if nfl_player_boxscore.rush_attempts > 0:
        assert f"while rushing {nfl_player_boxscore.rush_attempts} times" in news
        assert _nfl_rushing_stat_summary(nfl_player_boxscore) in news
    else:
        assert f"rush" not in news


@pytest.mark.parametrize(
    "stats",
    [
        {
            "field_goals_attempted": 3,
            "field_goals_made": 2,
            "extra_points_attempted": 2,
            "extra_points_made": 2,
        },
        {
            "extra_points_attempted": 2,
            "extra_points_made": 1,
        },
        {
            "field_goals_attempted": 4,
            "field_goals_made": 4,
        },
    ],
)
def test_write_nfl_player_news_for_ks(boxscore, player, nfl_player_boxscore, stats):
    player.position = "K"
    nfl_player_boxscore.configure_mock(**stats)
    news = write_nfl_player_news(boxscore, player, nfl_player_boxscore)
    if nfl_player_boxscore.field_goals_attempted:
        assert (
            f"{player_name} made {nfl_player_boxscore.field_goals_made} of {nfl_player_boxscore.field_goals_attempted} "
            "field goals" in news
        )
    else:
        assert "field goals" not in news
    if nfl_player_boxscore.extra_points_attempted > 0:
        assert (
            f"{nfl_player_boxscore.extra_points_made} for {nfl_player_boxscore.extra_points_attempted} on PATs" in news
        )
    else:
        assert "PATs" not in news
