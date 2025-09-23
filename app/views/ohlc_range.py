from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.views import APIView
from django.utils.dateparse import parse_datetime
from django.db.models import Q

from app.adapters.base_adapter import BaseAdapter, Period
from app.adapters.factory import get_adapter_for_datasource
from app.models import DataSource, Stock


@dataclass
class OHLCFilter:
    symbol: Optional[str] = None
    datasource: Optional[str] = None
    start: Optional[Any] = None
    end: Optional[Any] = None
    period: Optional[Period | str] = None
    meta: Optional[Dict[str, Any]] = None

    @classmethod
    def from_request(cls, request: Request) -> 'OHLCFilter':
        qp = request.query_params
        symbol = qp.get('symbol')
        datasource = qp.get('datasource')
        start_raw = qp.get('start')
        end_raw = qp.get('end')
        meta = qp.get('meta')

        start_dt = parse_datetime(start_raw) if start_raw else None
        end_dt = parse_datetime(end_raw) if end_raw else None

        return cls(symbol, datasource, start_dt, end_dt, meta)


class OHLCRangeAPIView(APIView):
    """Return OHLC for a symbol across datasources or a single datasource.

    Query params:
      symbol (required) - stock symbol
      datasource (optional) - datasource name or id
      start, end (optional) - ISO datetimes
    """

    def get(self, request: Request) -> Response:
        # parse filters from request
        filters = OHLCFilter.from_request(request)
        if not filters.symbol:
            return Response({'detail': 'symbol is required'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        if not filters.datasource:
            return Response({'detail': 'datsource is required'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # get datasource
        try:
            datasource = DataSource.objects.get(
                Q(id=int(filters.datasource)) 
                | Q(name=filters.datasource))
        except Exception:
            return Response({'detail': 'datasource not found'}, 
                            status=status.HTTP_404_NOT_FOUND)

        # get stock object
        stock = Stock.objects.filter(symbol__iexact=filters.symbol,
                                     datasource=datasource)
        if not stock.exists():
            return Response({'detail': 'symbol not found in datasource'}, 
                            status=status.HTTP_404_NOT_FOUND)

        # get adapter
        adapter = get_adapter_for_datasource(datasource)


        # fetch OHLC data
        ohlc_data = list(adapter.fetch_ohlc(
            symbol=filters.symbol,
            period=filters.period,
            start=filters.start,
            end=filters.end
        ))
        if ohlc_data:
            return Response(ohlc_data)
        else:
            return Response({'detail': 'no data found'}, 
                            status=status.HTTP_404_NOT_FOUND)
