from typing import Any, Dict
from rest_framework import serializers
from .models import DataSource, Stock, OHLC


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = '__all__'


class StockSerializer(serializers.ModelSerializer):
    datasource: DataSourceSerializer = DataSourceSerializer(read_only=True)

    class Meta:
        model = Stock
        fields = '__all__'


class OHLCSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OHLC
        fields = ('timestamp', 'open', 'high', 'low', 'close', 'volume')
