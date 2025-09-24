from __future__ import annotations

from typing import Any, Dict, Iterator, Optional
from datetime import datetime

from pandas import DataFrame

from app.adapters import factory
from app.adapters.base_adapter import BaseAdapter
from app.apis.base_api_client import BaseApiClient

from app.apis.factory import get as get_api

class RestAPIAdapter(BaseAdapter):
    """Adapter that wraps a `BaseApiClient` implementation.

    config expects:
      - api_key: API key for the client
    """

    def __init__(self, client: BaseApiClient):
        self.client = client

    def fetch_ohlc(
        self,
        symbol: str,
        period: str,
        start: datetime = None,
        end: datetime = None,
    ) -> Iterator[Dict[str, Any]]:
        # Convert Period to string
        timespan = period

        # BaseApiClient returns a DataFrame; call fetch_symbol
        df: DataFrame = self.client.fetch_symbol(
            symbol, from_=start, to=end, timespan=timespan
        )

        if df is None or df.empty:
            return iter([])

        # Expect DataFrame with columns: timestamp / t, o,h,l,c,v
        def _iter_rows():
            for _, row in df.iterrows():
                # try common column names
                ts = None
                if 'timestamp' in row.index:
                    ts = row['timestamp']
                elif 't' in row.index:
                    ts = row['t']

                yield {
                    'timestamp': ts,
                    'open': float(row.get('open') or row.get('o')),
                    'high': float(row.get('high') or row.get('h')),
                    'low': float(row.get('low') or row.get('l')),
                    'close': float(row.get('close') or row.get('c')),
                    'volume': int(row.get('volume') or row.get('v') or 0),
                }

        return _iter_rows()

    @classmethod
    def from_config(cls, cfg: Dict[str, Any]) -> "RestAPIAdapter":
        """Construct adapter from config dictionary."""
        api_cfg = cfg.get('api')
        if not api_cfg:
            raise ValueError("Missing 'api' in config for RestAPIAdapter")
        api_name = api_cfg.get('name')
        if not api_name:
            raise ValueError("Missing 'name' in 'api' config for RestAPIAdapter")
        
        api = get_api(api_name, api_cfg)
        
        return RestAPIAdapter(client=api)


factory.register_adapter('restapi', RestAPIAdapter.from_config)