import argparse
from dateutil import parser
import logging

from sportblurbs.database import BLURB_COLLECTION, get_database, put_documents
from sportblurbs.filter import filter_nfl_at_least_one_att
from sportblurbs.league import NFL, MLB, NBA
from sportblurbs.utils import create_blurb_documents
from sportblurbs.writer import write_player_blurbs_from_day

logger = logging.getLogger()

LEAGUE_MAP = {
    "NFL": NFL,
    "MLB": MLB,
    "NBA": NBA,
}
DATABASE = "sportblurbsdb"
TABLE = "playerblurbs"


def parse_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-d", "--date", action="store")
    arg_parser.add_argument("-l", "--league", action="store")
    args = arg_parser.parse_args()

    try:
        league = LEAGUE_MAP[args.league.upper()]
    except KeyError:
        logger.error("Unknown league '{}'.".format(args.league))
        raise

    return {"date": parser.parse(args.date), "league": league}


if __name__ == "__main__":
    # kwargs = parse_args()
    kwargs = {"date": (7, 2021), "league": NFL}
    # kwargs = {"date": parser.parse("2021-10-25"), "league": NBA}
    print("Writing player blurbs...")
    blurbs = write_player_blurbs_from_day(**kwargs, filters=filter_nfl_at_least_one_att)
    source = "sports-reference.com"
    print("Creating blurb docs...")
    blurb_docs = create_blurb_documents(blurbs, source, kwargs["league"])
    database = get_database()
    print("Putting blurbs into database...")
    put_documents(database, BLURB_COLLECTION, blurb_docs)
