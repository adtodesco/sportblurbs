import datetime

from pymongo import MongoClient

from sportblurbs.utils import game_is_complete

SPORTBLURBS_DB = "sportblurbsdb"
BLURB_COLLECTION = "blurb"
GAME_COLLECTION = "game"


def get_database(database_name=SPORTBLURBS_DB, connection_string="mongodb://localhost:27017/"):
    client = MongoClient(connection_string)
    return client[database_name]


def get_documents(database, collection_name, filters=None):
    # TODO: Implement me
    if filters:
        # Just putting this here for now so Pycharm doesn't warn me about documents always being None
        return list()

    return None


def get_document(database, colection_name, filters=None):
    documents = get_documents(database, colection_name, filters)
    if not documents:
        return None

    if len(documents) > 1:
        raise Exception()  # TODO: Raise MultipleDocumentError (or something like that)

    return documents[0]


def put_documents(database, collection_name, documents, unique_field=None, update=False):
    # TODO: Add logic to update documents that already exist when update is True
    database[collection_name].insert_many(documents)


def create_blurb_document(blurb, source, league):
    player = blurb["player"]
    return {
        "date": datetime.datetime.utcnow(),
        "player": {
            "id": player.player_id,
            "name": player.name,  # sportsipy stores single name - should we split it to first & last?
            "position": player.position.upper(),
            "team": player.team_abbreviation.upper(),
            "league": league.name,
        },
        "blurb": {"source": source, "news": blurb["news"], "spin": blurb["spin"]},
    }


def create_blurb_documents(blurbs, source, league):
    blurb_documents = list()
    for blurb in blurbs:
        blurb_documents.append(create_blurb_document(blurb, source, league))

    return blurb_documents


def create_game_document(boxscore, league, processed=False):
    # Should we do it like this, or should we have "home": {"team": <abbrev>, "score": <points>}, "away" {...} ?
    return {
        "date": datetime.datetime.utcnow(),
        "game": {
            "id": boxscore._uri,
            "date": boxscore.date,
            "teams": [
                {
                    "name": boxscore.winning_name,
                    "abbreviation": boxscore.winning_abbr.upper(),
                    "score": boxscore.home_points,
                    "is_home": boxscore.winning_name == boxscore._home_name.text(),
                },
                {
                    "name": boxscore.losing_name,
                    "abbreviation": boxscore.losing_abbr.upper(),
                    "score": boxscore.away_points,
                    "is_home": boxscore.losing_name == boxscore._home_name.text(),
                },
            ],
            "league": league.name,
        },
        "complete": game_is_complete(boxscore),
        "processed": processed,
    }


def create_game_documents(boxscores, league, processed=False):
    game_documents = list()
    for boxscore in boxscores:
        game_documents.append(create_game_document(boxscore, league, processed))

    return game_documents
