from datetime import datetime
import pandas as pd

from app.apis import factory as apifactory
from app.adapters import factory as adapterfactory

# Import RestAPIAdapter so it registers itself with adapters.factory
from app.adapters.rest_api_adapter import RestAPIAdapter


class DummyApiClient:
    def __init__(self, cfg):
        self.cfg = cfg

    def has_symbol(self, symbol: str) -> bool:
        return True

    def fetch_symbol(self, symbol, from_, to, timespan):
        return pd.DataFrame([
            {'timestamp': datetime(2025, 3, 1), 'o': 5.0, 'h': 6.0, 'l': 4.5, 'c': 5.5, 'v': 1000},
        ])


def test_factories_create_rest_api_adapter():
    # Register dummy API client under name 'dummy'
    apifactory.register_api('dummy', lambda cfg: DummyApiClient(cfg))

    # Create a datasource-like object
    class DS:
        name = 'restapi'
        type = 'restapi'
        config = {
            'api': {'name': 'dummy', 'api_key': 'X'},
        }

    ds = DS()

    adapter = adapterfactory.get_adapter_for_datasource(ds)
    rows = list(adapter.fetch_ohlc('FOO', '1d', start=None, end=None))
    assert len(rows) == 1
    assert rows[0]['open'] == 5.0
    assert rows[0]['volume'] == 1000
