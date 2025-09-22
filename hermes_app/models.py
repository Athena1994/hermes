from django.db import models
from typing import Any


class DataSource(models.Model):
    # type: 'web' or 'csv' or custom
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=50)
    config = models.JSONField(default=dict)
    enabled = models.BooleanField(default=True)

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
