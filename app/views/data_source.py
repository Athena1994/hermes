
from rest_framework import viewsets

from app.models import DataSource
from app.serializers import DataSourceSerializer


class DataSourceViewSet(viewsets.ModelViewSet):
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer