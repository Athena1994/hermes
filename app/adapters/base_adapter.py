from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator
from datetime import datetime

class BaseAdapter(ABC):
    """Base adapter interface for data sources."""

    @abstractmethod
    def fetch_ohlc(
        self,
        symbol: str,
        period: str,
        start: datetime = None,
        end: datetime = None,
    ) -> Iterator[dict[str]]:
        """Yield OHLC rows as dicts: {timestamp, open, high, low, close, volume}
        """

    