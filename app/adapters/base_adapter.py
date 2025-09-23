from abc import ABC, abstractmethod
from enum import Enum
from typing import Iterable, Dict, Any, Iterator, Optional, Union
from datetime import datetime

from app.models import Symbol

class Period(Enum):
    TICK = 'tick'
    ONE_MINUTE = '1m'
    FIVE_MINUTES = '5m'
    FIFTEEN_MINUTES = '15m'
    ONE_HOUR = '1h'
    FOUR_HOURS = '4h'
    ONE_DAY = '1d'
    ONE_WEEK = '1w'
    ONE_MONTH = '1mo'

class BaseAdapter(ABC):
    """Base adapter interface for data sources."""

    @abstractmethod
    def list_symbols(self) -> Iterable[Symbol]:
        """Return iterable of symbols offered by this datasource."""

    @abstractmethod
    def fetch_ohlc(self, symbol: str, 
                   period: Period | str,
                   start: datetime = None, 
                   end: datetime = None) -> Iterator[dict[str, Any]]:
        """Yield OHLC rows as dicts: {timestamp, open, high, low, close, volume} """

    