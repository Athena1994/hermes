from django.urls import path, include
from rest_framework import routers
from app import views
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.urls import include as _include

router = routers.DefaultRouter()
router.register(r'datasources', views.DataSourceViewSet)
router.register(r'stocks', views.StockViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/ohlc/', 
         views.OHLCRangeAPIView.as_view(), name='ohlc-range'),
    path('api/schema/', 
         SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', 
         SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', 
         SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
     path('api/stockdata/', _include('stockdata.urls')),
]
