from abc import ABC, abstractmethod
from typing import Iterable, Dict, Any, Iterator, Optional, Union
from datetime import datetime


class BaseAdapter(ABC):
    """Base adapter interface for data sources."""

    @abstractmethod
    def list_symbols(self) -> Iterable[Dict[str, Any]]:
        """Return iterable of {symbol, name} offered by this datasource."""

    @abstractmethod
    def fetch_ohlc(self, symbol: str, start: Optional[datetime] = None, end: Optional[datetime] = None) -> Iterator[Dict[str, Any]]:
        """Yield OHLC rows as dicts: {timestamp, open, high, low, close, volume} """


class CSVAdapter(BaseAdapter):
    def __init__(self, path: str, timezone: str = 'UTC'):
        self.path = path
        self.timezone = timezone

    def list_symbols(self) -> Iterator[Dict[str, Any]]:
        # For simple CSV files, treat filename as symbol
        import os
        yield {'symbol': os.path.splitext(os.path.basename(self.path))[0], 'name': os.path.basename(self.path)}

    def fetch_ohlc(self, symbol: str, start: Optional[datetime] = None, end: Optional[datetime] = None) -> Iterator[Dict[str, Any]]:
        # simple CSV loader; expects columns: timestamp,open,high,low,close,volume
        import csv
        from datetime import datetime as _dt
        with open(self.path, 'r', newline='') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                ts = _dt.fromisoformat(row['timestamp'])
                yield {
                    'timestamp': ts,
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row.get('volume') or 0)
                }


    def get_adapter_for_datasource(datasource: Union[Dict[str, Any], Any]) -> BaseAdapter:
        """Return an adapter instance for a DataSource model or dict-like with 'type' and 'config'.

        datasource: can be a Django model instance with .type and .config (JSONField), or a dict
        with keys 'type' and 'config'.
        """
        ds_type: Optional[str] = getattr(datasource, 'type', None) or (datasource.get('type') if isinstance(datasource, dict) else None)
        config: Dict[str, Any] = getattr(datasource, 'config', None) or (datasource.get('config') if isinstance(datasource, dict) else {})

        if ds_type == 'csv':
            path = config.get('path')
            return CSVAdapter(path=path, timezone=config.get('timezone', 'UTC'))

        # Placeholder for web adapters or others
        class WebAdapter(BaseAdapter):
            def __init__(self, cfg: Dict[str, Any]):
                self.cfg = cfg

            def list_symbols(self) -> Iterator[Dict[str, Any]]:
                return iter([])

            def fetch_ohlc(self, symbol: str, start: Optional[datetime] = None, end: Optional[datetime] = None) -> Iterator[Dict[str, Any]]:
                raise NotImplementedError('WebAdapter not implemented')

        return WebAdapter(config)
