from django.urls import path
from . import views

urlpatterns = [
    path('ohlc/', views.PolygonOHLCAPIView.as_view(), name='polygon-ohlc'),
]
