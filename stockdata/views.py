from typing import Any, Dict, List, Optional
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_datetime

from .api_client import StockDataApiClient


class StockDataOHLCAPIView(APIView):
    """Proxy endpoint to fetch OHLC from stockdata.org for a single symbol.

    Query params: symbol (required), start, end (ISO date strings)
    """

    def get(self, request, format: Optional[str] = None) -> Response:
        symbol = request.query_params.get('symbol')
        if not symbol:
            return Response({'detail': 'symbol is required'},
                            status=status.HTTP_400_BAD_REQUEST)
        start = request.query_params.get('start')
        end = request.query_params.get('end')

        try:
            client = StockDataApiClient()
        except RuntimeError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        rows: List[Dict[str, Any]] = []
        try:
            for item in client.ohlc(symbol=symbol, start=start, end=end):
                rows.append(item)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        if not rows:
            return Response({'detail': 'no data found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(rows)
