

import abc
from abc import abstractmethod
from datetime import datetime

from pandas import DataFrame


class BaseApiClient(abc.ABC):
    """Base API client interface for external services."""

    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout

    @abstractmethod
    def has_symbol(self, symbol: str) -> bool:
        """Return True if the symbol is known to this datasource."""

    @abstractmethod
    def fetch_symbol(self, symbol: str, 
                     from_: datetime, to: datetime,
                     timespan: str) -> DataFrame:
        """Return metadata dict for `symbol`."""