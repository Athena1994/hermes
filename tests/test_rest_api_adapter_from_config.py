from datetime import datetime
import pandas as pd

from app.apis import factory as apifactory
from app.adapters.rest_api_adapter import RestAPIAdapter


class DummyApiClient2:
    def __init__(self, cfg):
        self.cfg = cfg

    def has_symbol(self, symbol: str) -> bool:
        return True

    def fetch_symbol(self, symbol, from_, to, timespan):
        return pd.DataFrame([
            {'timestamp': datetime(2025, 4, 1), 'open': 7.0, 'high': 8.0, 'low': 6.5, 'close': 7.5, 'volume': 500},
        ])


def test_rest_api_adapter_from_config():
    # register dummy api
    apifactory.register_api('dummy2', lambda cfg: DummyApiClient2(cfg))

    cfg = {
        'api': {'name': 'dummy2', 'api_key': 'Y'},
    }

    adapter = RestAPIAdapter.from_config(cfg)
    rows = list(adapter.fetch_ohlc('BAZ', '1d', start=None, end=None))
    assert len(rows) == 1
    assert rows[0]['open'] == 7.0
    assert rows[0]['volume'] == 500
