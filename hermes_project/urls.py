from django.urls import path, include
from rest_framework import routers
from hermes_app import views

router = routers.DefaultRouter()
router.register(r'datasources', views.DataSourceViewSet)
router.register(r'stocks', views.StockViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/ohlc/', views.OHLCRangeAPIView.as_view(), name='ohlc-range'),
]
