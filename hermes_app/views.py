from typing import Any, Dict, Iterable, List, Optional

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django.db.models import Q

from .models import DataSource, Stock, OHLC
from .serializers import DataSourceSerializer, StockSerializer, OHLCSimpleSerializer
from .adapters import get_adapter_for_datasource, BaseAdapter


class DataSourceViewSet(viewsets.ModelViewSet):
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer


class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.select_related('datasource').all()
    serializer_class = StockSerializer

    @action(detail=False, methods=['get'])
    def by_symbol(self, request) -> Response:
        symbol = request.query_params.get('symbol')
        if not symbol:
            return Response({'detail': 'symbol query param required'}, status=status.HTTP_400_BAD_REQUEST)
        stocks = self.queryset.filter(symbol__iexact=symbol)
        serializer = self.get_serializer(stocks, many=True)
        return Response(serializer.data)


class OHLCRangeAPIView(APIView):
    """Return OHLC for a symbol across datasources or a single datasource.

    Query params:
      symbol (required) - stock symbol
      datasource (optional) - datasource name or id
      start, end (optional) - ISO datetimes
    """

    def get(self, request, format=None) -> Response:
        symbol: Optional[str] = request.query_params.get('symbol')
        if not symbol:
            return Response({'detail': 'symbol is required'}, status=status.HTTP_400_BAD_REQUEST)

        datasource_q: Optional[str] = request.query_params.get('datasource')
        start: Optional[str] = request.query_params.get('start')
        end: Optional[str] = request.query_params.get('end')

        start_dt = parse_datetime(start) if start else None
        end_dt = parse_datetime(end) if end else None

        # If a datasource filter is provided, prefer that. Otherwise, try to find configured stocks.
        qs = Stock.objects.filter(symbol__iexact=symbol)
        ds = None
        if datasource_q:
            # allow numeric pk or name
            try:
                ds = DataSource.objects.get(Q(id=int(datasource_q)) | Q(name=datasource_q))
            except Exception:
                return Response({'detail': 'datasource not found'}, status=status.HTTP_404_NOT_FOUND)
            stocks = qs.filter(datasource=ds)
        else:
            stocks = qs

        # If we have any matching stocks in DB and they have OHLC stored, return those ranges first.
        results: List[Dict[str, Any]] = []
        for stock in stocks:
            ohlc_qs = OHLC.objects.filter(stock=stock)
            if start_dt:
                ohlc_qs = ohlc_qs.filter(timestamp__gte=start_dt)
            if end_dt:
                ohlc_qs = ohlc_qs.filter(timestamp__lte=end_dt)
            ohlc_qs = ohlc_qs.order_by('timestamp')[:10000]
            if ohlc_qs.exists():
                serializer = OHLCSimpleSerializer(ohlc_qs, many=True)
                results.extend(serializer.data)

        if results:
            return Response(results)

        # Otherwise, fallback to adapters (live fetch). Use configured datasources matching the stocks or all datasources.
        adapters: List[BaseAdapter] = []
        if ds is not None:
            adapters = [get_adapter_for_datasource(ds)]
        else:
            # build adapters for datasources associated with symbol
            ds_ids = set(s.datasource_id for s in stocks if s.datasource_id)
            if ds_ids:
                adapters = [get_adapter_for_datasource(DataSource.objects.get(id=dsid)) for dsid in ds_ids]
            else:
                adapters = [get_adapter_for_datasource(ds) for ds in DataSource.objects.filter(enabled=True)]

        # Query adapters in order until we get results
        for adapter in adapters:
            try:
                fetcher = adapter.fetch_ohlc(symbol=symbol, start=start_dt, end=end_dt)
                for item in fetcher:
                    # adapter returns dict-like rows; keep them as-is for the API
                    results.append(item)
                if results:
                    return Response(results)
            except Exception as exc:
                # log and continue
                print('adapter error', exc)
                continue

        return Response({'detail': 'no data found'}, status=status.HTTP_404_NOT_FOUND)
