from django.urls import path
from . import views

urlpatterns = [
    path('ohlc/', views.StockDataOHLCAPIView.as_view(), name='stockdata-ohlc'),
]
