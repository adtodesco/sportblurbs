import logging

from sportblurbs.database import (
    get_database,
    get_document,
    GAME_COLLECTION,
    put_documents,
    BLURB_COLLECTION,
    create_blurb_documents,
    create_game_document,
)
from sportblurbs.utils import game_is_complete
from sportblurbs.writer import BasicPlayerNewsWriter, NullSpinWriter, write_player_blurbs_from_boxscore


logger = logging.getLogger()


def process_games(dates, league, news_writer=BasicPlayerNewsWriter(), spin_writer=NullSpinWriter(), filters=None):
    logger.info("Gathering boxscores...")
    boxscores = list()
    for date in dates:
        print(f"date: {league.date_string(date)}")  # TODO: remove
        boxscores.extend(league.get_boxscores(date))

    database = get_database()
    logger.info("Writing player blurbs...")
    blurbs = list()
    new_or_updated_boxscores = dict()
    for boxscore in boxscores:
        print(f"boxscore: {str(boxscore)}")  # TODO: remove
        game_doc = get_document(database, GAME_COLLECTION, {"game.id": boxscore._uri})
        if not game_doc:
            game_doc = create_game_document(boxscore, league)
            new_or_updated_boxscores.update({boxscore._uri: game_doc})
        game_doc["complete"] = game_is_complete(boxscore)
        if game_doc["complete"] and not game_doc["processed"]:
            blurbs.extend(write_player_blurbs_from_boxscore(boxscore, league, news_writer, spin_writer, filters))
            game_doc["processed"] = True
            new_or_updated_boxscores.update({boxscore._uri: game_doc})

    # TODO: Add logic to reset database states on failures? Or at least retry retry-able failures and log info to fix.
    source = "sports-reference.com"
    if blurbs:
        logger.info("Creating blurb docs...")
        blurb_docs = create_blurb_documents(blurbs, source, league)
        logger.info("Putting blurbs into database...")
        put_documents(database, BLURB_COLLECTION, blurb_docs)
    else:
        logger.info("No blurbs written.")
    if new_or_updated_boxscores:
        logger.info("Putting new and updated games into database...")
        put_documents(database, GAME_COLLECTION, new_or_updated_boxscores.values(), update=True)
    else:
        logger.info("No new or updated games.")
    logger.info("Processing complete.")
