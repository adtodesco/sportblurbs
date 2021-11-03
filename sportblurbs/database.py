from pymongo import MongoClient

SPORTBLURBS_DB = "sportblurbsdb"
BLURB_COLLECTION = "blurb"
GAME_COLLECTION = "game"


def get_database(database_name=SPORTBLURBS_DB, connection_string="mongodb://localhost:27017/"):
    client = MongoClient(connection_string)
    return client[database_name]


def put_documents(database, collection_name, documents):
    database[collection_name].insert_many(documents)
