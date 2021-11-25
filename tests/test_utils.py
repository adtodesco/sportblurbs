import copy
import pytest
from unittest import mock

from sportblurbs.exception import KeyNotFoundError
from sportblurbs.utils import get_value_from_document


documents = [
    {"keyA": {"keyB": [1, 2, 3]}, "keyC": "valC"},
    {"keyD": {"keyE": [1, 2, 3]}, "keyF": "valF"},
]


@pytest.mark.parametrize("key", ["keyX.keyY", "keyZ"])
@pytest.mark.parametrize("document", documents)
def test_get_value_from_document_raises_key_not_found_error_when_key_does_not_exist(document, key):
    with pytest.raises(KeyNotFoundError, match=key):
        get_value_from_document(key, document)


@pytest.mark.parametrize(
    "document,key,expected_value",
    [
        (documents[0], "keyA", documents[0]["keyA"]),
        (documents[0], "keyA.keyB", documents[0]["keyA"]["keyB"]),
        (documents[1], "keyD.keyE", documents[1]["keyD"]["keyE"]),
    ],
)
def test_get_value_from_document_returns_value(document, key, expected_value):
    assert get_value_from_document(key, document) == expected_value
