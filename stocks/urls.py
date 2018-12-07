from django.urls import path

from .views import (CompanyDetailView, CompanyListView,
                    StockPeriodsAnalyticsView, StockPriceAnalyticsView,
                    TradeInsiderListView, TradeListView)

urlpatterns = [
    path(
        '',
        CompanyListView.as_view(), name='companies-list'
    ),
    path(
        '<slug:ticker>/',
        CompanyDetailView.as_view(), name='company-detail'
    ),
    path(
        '<slug:ticker>/insider/',
        TradeListView.as_view(), name='trades-list'
    ),
    path(
        '<slug:ticker>/insider/<slug:insider>/',
        TradeInsiderListView.as_view(), name='insider-trades-list'
    ),
    path(
        '<slug:ticker>/analytics/',
        StockPriceAnalyticsView.as_view(), name='stock-analytics'
    ),
    path(
        '<slug:ticker>/delta/',
        StockPeriodsAnalyticsView.as_view(), name='stock-delta'
    )
]
