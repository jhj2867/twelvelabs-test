import pytest
from utils.client import get_client
from utils.config import INDEX_ID


@pytest.fixture(scope="session")
def client():
    return get_client()


@pytest.fixture(scope="session")
def index_id():
    return INDEX_ID