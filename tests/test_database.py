import copy

import pytest
from unittest import mock

from sportblurbs.database import (
    create_blurb_documents,
    create_game_documents,
    get_document,
    update_documents,
    BLURB_COLLECTION,
    GAME_COLLECTION,
    SPORTBLURBS_DB,
)
from sportblurbs.exception import MultipleDocumentsError
from sportblurbs.league import League
from sportblurbs.utils import get_value_from_document

league_name = "SLN"
season_start = (6, 1)
game_collection_len = 5
blurb_collection_len = 5
blurb_source = "sportblurb-source.com"
database_name = "database-name"


@pytest.fixture
def league():
    return League(
        name=league_name,
        league_module=mock.MagicMock(),
        season_start=season_start,
    )


@pytest.fixture
def boxscores():
    mock_boxscore = mock.Mock()
    mock_boxscore.home_points = 10
    mock_boxscore.away_points = 0
    return [copy.deepcopy(mock_boxscore) for _ in range(game_collection_len)]


@pytest.fixture
def game_collection(boxscores, league):
    return create_game_documents(boxscores, league)


@pytest.fixture
def blurbs():
    return [mock.MagicMock() for _ in range(blurb_collection_len)]


@pytest.fixture
def blurb_collection(blurbs, league):
    return create_blurb_documents(blurbs, blurb_source, league)


@pytest.fixture
def sportblurbs_database(game_collection, blurb_collection):
    mock_game_collection = mock.Mock()
    mock_game_collection.find.return_value = game_collection
    mock_game_collection.count_documents.return_value = len(game_collection)
    mock_blurb_collection = mock.Mock()
    mock_blurb_collection.find.return_value = blurb_collection
    mock_blurb_collection.count_documents.return_value = len(blurb_collection)
    mock_sportblurbs_database_dict = {GAME_COLLECTION: mock_game_collection, BLURB_COLLECTION: mock_blurb_collection}
    mock_sportblurbs_database = mock.MagicMock()
    mock_sportblurbs_database.__getitem__.side_effect = mock_sportblurbs_database_dict.__getitem__
    mock_sportblurbs_database.name = SPORTBLURBS_DB
    return mock_sportblurbs_database


@pytest.mark.parametrize("collection_name", [GAME_COLLECTION, BLURB_COLLECTION])
def test_get_document_returns_none_when_no_matching_documents(sportblurbs_database, collection_name):
    sportblurbs_database[collection_name].count_documents.return_value = 0
    sportblurbs_database[collection_name].find.return_value = list()
    assert get_document(sportblurbs_database, collection_name) is None


@pytest.mark.parametrize("collection_name", [GAME_COLLECTION, BLURB_COLLECTION])
def test_get_document_raises_error_when_multiple_matching_documents(sportblurbs_database, collection_name):
    with pytest.raises(MultipleDocumentsError):
        assert get_document(sportblurbs_database, collection_name)


@pytest.mark.parametrize("collection_name", [GAME_COLLECTION, BLURB_COLLECTION])
def test_get_document_returns_matching_document(sportblurbs_database, collection_name):
    mock_document = mock.Mock()
    sportblurbs_database[collection_name].count_documents.return_value = 1
    sportblurbs_database[collection_name].find.return_value = [mock_document]
    assert get_document(sportblurbs_database, collection_name) == mock_document


@pytest.mark.parametrize("collection_name", [GAME_COLLECTION, BLURB_COLLECTION])
def test_update_documents_raises_multiple_documents_error_when_key_is_not_unique(sportblurbs_database, collection_name):
    documents = copy.deepcopy(sportblurbs_database[collection_name].find())
    non_unique_key = list(documents[0])[0]
    sportblurbs_database[collection_name].count_documents.return_value = 2
    with pytest.raises(MultipleDocumentsError, match=non_unique_key):
        update_documents(sportblurbs_database, collection_name, documents, non_unique_key)


@pytest.mark.parametrize("collection_name", [GAME_COLLECTION, BLURB_COLLECTION])
def test_update_documents_updates_documents(sportblurbs_database, collection_name):
    documents = copy.deepcopy(sportblurbs_database[collection_name].find())
    unique_key = list(documents[0])[0]
    sportblurbs_database[collection_name].count_documents.return_value = 1
    update_documents(sportblurbs_database, collection_name, documents, unique_key)
    update_calls = list()
    for call_args in sportblurbs_database[collection_name].update_one.call_args_list:
        filter = call_args[0][0]
        document = call_args[0][1]
        update_calls.append((filter, document))

    for document in documents:
        filter = {unique_key: get_value_from_document(unique_key, document)}
        assert (filter, document) in update_calls
