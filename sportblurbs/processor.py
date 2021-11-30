import logging

from sportblurbs.database import (
    create_blurb_documents,
    create_game_document,
    get_database,
    get_document,
    put_documents,
    update_documents,
    GAME_COLLECTION,
    BLURB_COLLECTION,
)
from sportblurbs.utils import game_is_complete
from sportblurbs.writer import write_generic_player_news, write_null_spin, write_player_blurbs_from_boxscore


logger = logging.getLogger()


def process_games(dates, league, new_func=write_generic_player_news, spin_func=write_null_spin, filters=None):
    logger.info("Getting boxscores...")
    boxscores = list()
    for date in dates:
        logger.debug(f"Getting boxscores from '{league.date_string(date)}'.")
        boxscores.extend(league.get_boxscores(date))

    database = get_database()
    logger.info("Writing player blurbs...")
    blurbs = list()
    new_or_updated_boxscores = dict()
    for boxscore in boxscores:
        logger.debug(f"Checking document for '{str(boxscore)}'.")
        game_doc = get_document(database, GAME_COLLECTION, {"game.id": boxscore._uri})
        if not game_doc:
            game_doc = create_game_document(boxscore, league)
            new_or_updated_boxscores.update({boxscore._uri: game_doc})
        game_doc["complete"] = game_is_complete(boxscore)
        if game_doc["complete"] and not game_doc["processed"]:
            blurbs.extend(write_player_blurbs_from_boxscore(boxscore, league, new_func, spin_func, filters))
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
        update_documents(database, GAME_COLLECTION, new_or_updated_boxscores.values(), "game.id", upsert=True)
    else:
        logger.info("No new or updated games.")
    logger.info("Processing complete.")
