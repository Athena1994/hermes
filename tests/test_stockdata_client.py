from stockdata.api_client import StockDataApiClient
from datetime import datetime


def test_parse_date():
    c = StockDataApiClient(api_key='dummy')
    assert c._parse_date('2025-09-24T10:00:00') == datetime.fromisoformat('2025-09-24T10:00:00')
    assert c._parse_date(None) is None


def test_ohlc_pagination(monkeypatch):
    pages = [
        {'data': [{'date': '2025-01-01', 'open': 1, 'high': 2, 'low': 0, 'close': 1, 'volume': 10}],
         'meta': {'next_url': 'http://next'}},
        {'data': [{'date': '2025-01-02', 'open': 2, 'high': 3, 'low': 1, 'close': 2, 'volume': 20}],
         'meta': {}},
    ]

    def fake_get(url, params=None):
        return pages.pop(0)

    c = StockDataApiClient(api_key='dummy')
    monkeypatch.setattr(c, '_get_json', fake_get)
    rows = list(c.ohlc('FOO'))
    assert len(rows) == 2
