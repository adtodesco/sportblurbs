import datetime
from pymongo import MongoClient

from sportblurbs.exception import MultipleDocumentsError
from sportblurbs.utils import game_is_complete, game_score, get_value_from_document

SPORTBLURBS_DB = "sportblurbsdb"
BLURB_COLLECTION = "blurb"
GAME_COLLECTION = "game"


def get_database(database_name=SPORTBLURBS_DB, connection_string="mongodb://localhost:27017/"):
    client = MongoClient(connection_string)
    return client[database_name]


def get_documents(database, collection_name, filter=None):
    return database[collection_name].find(filter)[:]


def get_document(database, collection_name, filter=None):
    documents = get_documents(database, collection_name, filter)
    if not documents:
        return None
    if len(documents) > 1:
        raise MultipleDocumentsError(database.name, collection_name, filter)

    return documents[0]


def put_documents(database, collection_name, documents):
    if isinstance(documents, str):
        documents = [documents]
    database[collection_name].insert_many(documents)


def update_documents(database, collection_name, documents, unique_key, upsert=False):
    if isinstance(documents, str):
        documents = [documents]
    values = list()
    for document in documents:
        value = get_value_from_document(unique_key, document)
        doc_count = database[collection_name].count({unique_key: value})
        if doc_count > 1:
            raise MultipleDocumentsError(database.name, collection_name, f"{{{unique_key}: {value}}}")
        values.append(value)

    for document, value in zip(documents, values):
        database[collection_name].update_one({unique_key: value}, document, upsert=upsert)


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
    away_score, home_score = game_score(boxscore)
    winning_score, losing_score = (away_score, home_score) if away_score > home_score else (home_score, away_score)
    return {
        "date": datetime.datetime.utcnow(),
        "game": {
            "id": boxscore._uri,
            "date": boxscore.date,
            "teams": [
                {
                    "name": boxscore.winning_name,
                    "abbreviation": boxscore.winning_abbr.upper(),
                    "score": winning_score,
                    "is_home": boxscore.winning_name == boxscore._home_name.text(),
                },
                {
                    "name": boxscore.losing_name,
                    "abbreviation": boxscore.losing_abbr.upper(),
                    "score": losing_score,
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
