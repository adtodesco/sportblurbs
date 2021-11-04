import argparse
import datetime
from datetime import datetime, timedelta
from dateutil import parser
import logging
import sys

from sportblurbs.filter import (
    filter_nba_at_least_one_minute_played,
    filter_nfl_at_least_one_att,
    filter_player_has_position,
    filter_player_has_team,
)
from sportblurbs.league import NFL, MLB, NBA
from sportblurbs.processor import process_games

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()

LEAGUE_MAP = {
    "NFL": NFL,
    "MLB": MLB,
    "NBA": NBA,
}


def parse_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-s", "--start-date", action="store")
    arg_parser.add_argument("-e", "--end-date", action="store")
    arg_parser.add_argument("-l", "--league", action="store")
    args = arg_parser.parse_args()

    try:
        league = LEAGUE_MAP[args.league.upper()]
    except KeyError:
        logger.error("Unknown league '{}'.".format(args.league))
        raise

    dates = list()
    if league == NFL:
        pass  # TODO: Convert date range to week-year range
    else:
        start_date = parser.parse(args.start_date)
        end_date = parser.parse(args.end_date)
        if start_date > end_date:
            logger.error(f"start_date '{args.start_date}' is after end_date '{args.end_date}'.")
            exit(1)
        dates = [start_date + timedelta(t) for t in range((end_date - start_date).days)]

    print(f"start_date '{args.start_date}', end_date '{args.end_date}'.")
    print(f"dates {str(dates)}")

    return {"dates": dates, "league": league}


if __name__ == "__main__":
    # kwargs = parse_args()

    kwargs = {"dates": [(i, 2021) for i in range(8, 9)], "league": NFL}
    filters = [filter_nfl_at_least_one_att, filter_player_has_position, filter_player_has_team]

    # nba_start_dt = datetime(year=2021, month=11, day=1)
    # nba_days = range((datetime.today() - nba_start_dt).days)
    # kwargs = {"dates": [nba_start_dt + timedelta(days=d) for d in nba_days], "league": NBA}
    # filters = [filter_nba_at_least_one_minute_played, filter_player_has_position, filter_player_has_team]

    process_games(**kwargs, filters=filters)
