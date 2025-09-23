
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework import status

from app.models import Stock
from app.serializers import StockSerializer

class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.select_related('datasource').all()
    serializer_class = StockSerializer

    @action(detail=False, methods=['get'])
    def by_symbol(self, request: Request) -> Response:
        symbol = request.query_params.get('symbol')
        if not symbol:
            return Response({'detail': 'symbol query param required'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        stocks = self.queryset.filter(symbol__iexact=symbol)
        serializer = self.get_serializer(stocks, many=True)
        return Response(serializer.data)
