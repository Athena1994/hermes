from dataclasses import dataclass, field
from django.db import models
from typing import Any, Set


@dataclass(frozen=True)
class Symbol:
    """Core domain entity representing a tradable symbol."""
    symbol: str           # Unique identifier, e.g., "AAPL"
    name: str             # Human-readable name
    periods: Set[str]     # Available timeframes, e.g., {"1m", "5m", "1d"}
    metadata: dict[str, Any] = field(default_factory=dict)

class DataSource(models.Model):
    # type: 'web' or 'csv' or custom
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=50)
    config = models.JSONField(default=dict)
    enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ('name', 'type')

    def __str__(self):
        return f"{self.name} ({self.type})"


class Stock(models.Model):
    datasource = models.ForeignKey(DataSource, related_name='stocks', on_delete=models.CASCADE)
    symbol = models.CharField(max_length=50)
    name = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('datasource', 'symbol')

    def __str__(self):
        return f"{self.symbol} @ {self.datasource.name}"


class OHLC(models.Model):
    stock = models.ForeignKey(Stock, related_name='ohlc', on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.BigIntegerField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=['stock', 'timestamp'])]
        ordering = ['timestamp']
