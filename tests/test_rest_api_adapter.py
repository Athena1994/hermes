from datetime import datetime
import pandas as pd
from app.adapters.rest_api_adapter import RestAPIAdapter


class FakeClient:
    def __init__(self, api_key=None):
        pass

    def fetch_symbol(self, symbol, from_, to, timespan):
        # return DataFrame-like object
        df = pd.DataFrame([
            {'timestamp': datetime(2025, 1, 1), 'o': 1.0, 'h': 2.0, 'l': 0.5, 'c': 1.5, 'v': 100},
            {'timestamp': datetime(2025, 1, 2), 'o': 1.5, 'h': 2.1, 'l': 1.0, 'c': 1.9, 'v': 200},
        ])
        return df


def test_rest_api_adapter_conversion():
    client = FakeClient()
    adapter = RestAPIAdapter(client=client)
    rows = list(adapter.fetch_ohlc('FOO', '1d', start=None, end=None))
    assert len(rows) == 2
    assert rows[0]['open'] == 1.0
    assert rows[1]['volume'] == 200


def test_rest_api_adapter_full_column_names():
    class FullColsClient(FakeClient):
        def fetch_symbol(self, symbol, from_, to, timespan):
            import pandas as pd
            df = pd.DataFrame([
                {'timestamp': datetime(2025, 2, 1), 'open': 10.0, 'high': 11.0,
                 'low': 9.5, 'close': 10.5, 'volume': 123},
            ])
            return df

    client = FullColsClient()
    adapter = RestAPIAdapter(client=client)
    rows = list(adapter.fetch_ohlc('BAR', '1d', start=None, end=None))
    assert len(rows) == 1
    assert rows[0]['open'] == 10.0


def test_rest_api_adapter_empty_dataframe():
    class EmptyClient:
        def fetch_symbol(self, symbol, from_, to, timespan):
            import pandas as pd
            return pd.DataFrame([])

    client = EmptyClient()
    adapter = RestAPIAdapter(client=client)
    rows = list(adapter.fetch_ohlc('EMPTY', '1d', start=None, end=None))
    assert rows == []
