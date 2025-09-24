import os
import requests
from typing import Iterator, Dict, Any, Optional
from datetime import datetime

API_BASE = 'https://api.polygon.io'

class PolygonClient:
    """Thin client for Polygon.io - only a minimal EOD/AGG fetcher used by Hermes.

    Expects POLYGON_API_KEY env var or api_key passed.
    """

    def __init__(self, api_key: Optional[str] = None, timeout: int = 10):
        self.api_key = api_key or os.getenv('POLYGON_API_KEY')
        if not self.api_key:
            raise RuntimeError('POLYGON_API_KEY not set')
        self.timeout = timeout
        self.session = requests.Session()

    def aggs(self, symbol: str, start: str = None, end: str = None) -> Iterator[Dict[str, Any]]:
        """Yield aggregated bars using Polygon's /v2/aggs/ticker/{symbol}/range endpoint.

        Returns rows with keys compatible with Hermes OHLC representation.
        """
        params = {'adjusted': 'true', 'sort': 'asc', 'limit': 50000, 'apiKey': self.api_key}
        if start:
            params['from'] = start
        if end:
            params['to'] = end

        url = f'{API_BASE}/v2/aggs/ticker/{symbol}/range/1/day/{start}/{end}'
        resp = self.session.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get('results', []):
            yield {
                'timestamp': datetime.fromtimestamp(item.get('t') / 1000.0).isoformat(),
                'open': item.get('o'),
                'high': item.get('h'),
                'low': item.get('l'),
                'close': item.get('c'),
                'volume': item.get('v'),
            }
