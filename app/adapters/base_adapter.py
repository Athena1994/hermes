from abc import ABC, abstractmethod
from typing import Iterable, Dict, Any, Iterator, Optional, Union
from datetime import datetime

from app.models import Symbol


class BaseAdapter(ABC):
    """Base adapter interface for data sources."""

    @abstractmethod
    def list_symbols(self) -> Iterable[Symbol]:
        """Return iterable of symbols offered by this datasource."""

    @abstractmethod
    def fetch_ohlc(self, symbol: str, 
                   start: datetime = None, end: datetime = None) -> Iterator[dict[str, Any]]:
        """Yield OHLC rows as dicts: {timestamp, open, high, low, close, volume} """

    