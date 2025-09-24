import os
import requests
from typing import Dict, Any, Iterator, Optional
from datetime import datetime

API_BASE = 'https://api.stockdata.org/v1'


class StockDataApiClient:
    """Small wrapper for stockdata.org endpoints used by Hermes.

    Features:
      - session reuse with retries
      - pagination support (follows `meta.next_url` or `links.next`)
      - optional parsing of dates into `datetime` objects

    Expects env var STOCKDATA_API_KEY to be set or an api_key passed.
    """

    def __init__(self, api_key: str | None = None, timeout: int = 10):
        self.api_key = api_key or os.getenv('STOCKDATA_API_KEY')
        if not self.api_key:
            raise RuntimeError('STOCKDATA_API_KEY not set')
        self.timeout = timeout

        # session with retry/backoff
        self.session = requests.Session()
        try:
            from urllib3.util.retry import Retry
            from requests.adapters import HTTPAdapter

            retry = Retry(
                total=3,
                backoff_factor=0.3,
                status_forcelist=(429, 500, 502, 503, 504),
                allowed_methods=('GET',),
            )
            adapter = HTTPAdapter(max_retries=retry)
            self.session.mount('https://', adapter)
            self.session.mount('http://', adapter)
        except Exception:
            # gracefully continue without retries if urllib3 not available
            pass

    def _get_json(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        resp = self.session.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def _parse_date(self, value: Optional[str]) -> Optional[datetime]:
        if value is None:
            return None
        # try isoformat first
        try:
            return datetime.fromisoformat(value)
        except Exception:
            # try integer/float epoch seconds
            try:
                return datetime.fromtimestamp(float(value))
            except Exception:
                return None

    def ohlc(
        self,
        symbol: str,
        start: str | None = None,
        end: str | None = None,
        parse_dates: bool = False,
        limit: Optional[int] = None,
    ) -> Iterator[Dict[str, Any]]:
        """Yield OHLC rows for `symbol` using the /data/eod endpoint.

        Parameters:
          symbol: symbol string (e.g. 'MSFT')
          start/end: optional ISO date strings to bound results
          parse_dates: if True convert `date` field to datetime
          limit: optional maximum rows to fetch in total
        """
        params: Dict[str, Any] = {'symbols': symbol, 'api_token': self.api_key}
        if start:
            params['date_from'] = start
        if end:
            params['date_to'] = end
        if limit:
            params['limit'] = limit

        url = f'{API_BASE}/data/eod'
        fetched = 0
        while url:
            data = self._get_json(url, params)
            # reset params after first page (pagination urls contain params)
            params = {}

            for item in data.get('data', []):
                row = {
                    'timestamp': (
                        self._parse_date(item.get('date'))
                        if parse_dates
                        else item.get('date')
                    ),
                    'open': item.get('open'),
                    'high': item.get('high'),
                    'low': item.get('low'),
                    'close': item.get('close'),
                    'volume': item.get('volume'),
                }
                yield row
                fetched += 1
                if limit and fetched >= limit:
                    return

            # follow pagination links if present
            next_url = None
            meta = data.get('meta') or {}
            links = data.get('links') or {}
            next_url = meta.get('next_url') or meta.get('next') or links.get('next')
            url = next_url
