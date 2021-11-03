import datetime


def player_is_home(player, boxscore):
    return player.team_abbreviation.upper() == boxscore.home_abbreviation.upper()


def create_blurb_document(blurb, source, league=None):
    player = blurb["player"]
    return {
        "date": datetime.datetime.utcnow(),  # TODO: Is this the right format?
        "player": {
            "id": player.player_id,
            "name": player.name,
            "position": player.position,  # TODO: Figure out why position & team_abbreviation are empty
            "team": player.team_abbreviation,
            "league": league.name,
        },
        "blurb": {"source": source, "news": blurb["news"], "spin": blurb["spin"]},
    }


def create_blurb_documents(blurbs, source, league=None):
    blurb_documents = list()
    for blurb in blurbs:
        blurb_documents.append(create_blurb_document(blurb, source, league))

    return blurb_documents


def create_game_document(boxscore, complete, processed, league):
    return {
        "date": boxscore.datetime,
        "game": {
            "id": boxscore._uri,
            "teams": {"home": boxscore.home_abbr, "away": boxscore.away_abbr},
            "score": {"home": boxscore.home_score, "away": boxscore.away_score},
            "league": league.name,
        },
        "complete": complete,
        "processed": processed,
    }


def create_game_documents(boxscores, league=None):
    game_documents = list()
    for boxscore in boxscores:
        complete = False
        processed = False
        game_documents.append(create_game_document(boxscore, complete, processed, league))

    return game_documents
