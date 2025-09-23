
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Iterator

from app.models import Symbol
from app.adapters.base_adapter import BaseAdapter


class CSVAdapter(BaseAdapter):
    def __init__(self, path: Path, timezone: str = 'UTC'):
        self.path = path
        self.timezone = timezone

    def list_symbols(self) -> Iterator[Symbol]:
        # For simple CSV files, treat filename as symbol
        yield {
            'symbol': os.path.splitext(os.path.basename(self.path))[0],
            'name': os.path.basename(self.path),
        }

    def fetch_ohlc(
        self,
        symbol: str,
        start: datetime = None,
        end: datetime = None,
    ) -> Iterator[dict[str]]:
        # simple CSV loader; expects columns: timestamp,open,high,low,close,volume
        with open(self.path, 'r', newline='') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                ts = datetime.fromisoformat(row['timestamp'])
                yield {
                    'timestamp': ts,
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row.get('volume') or 0),
                }