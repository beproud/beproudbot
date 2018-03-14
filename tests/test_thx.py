import pytest
from tests.factories import thx
from tests.db import session
from haro.plugins.thx_models import ThxHistory


@pytest.fixture
def thx_histories():
    histories = thx.ThxHistoryFactory.create_batch(100)
    return histories


@pytest.mark.dbtest
def test_print_stuff(thx_histories):
    res = session.query(ThxHistory).all()
    assert set(res) == set(thx_histories)
