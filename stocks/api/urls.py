from django.urls import path

from .views import (CompanyListAPIView, StockDayListAPIView,
                    StockPeriodsAnalyticsAPIView, StockPriceAnalyticsAPIView,
                    TradeInsiderListAPIView, TradeListAPIView)

urlpatterns = [
    path('', CompanyListAPIView.as_view(), name='companies-list'),
    path(
        '<slug:ticker>/',
        StockDayListAPIView.as_view(), name='stocks-list'
    ),
    path(
        '<slug:ticker>/insider/',
        TradeListAPIView.as_view(), name='trades-list'
    ),
    path(
        '<slug:ticker>/insider/<slug:insider>/',
        TradeInsiderListAPIView.as_view(), name='insider-trades-list'
    ),
    path(
        '<slug:ticker>/analytics/',
        StockPriceAnalyticsAPIView.as_view(), name='stock-analytics'
    ),
    path(
        '<slug:ticker>/delta/',
        StockPeriodsAnalyticsAPIView.as_view(), name='stock-delta'
    ),
]
