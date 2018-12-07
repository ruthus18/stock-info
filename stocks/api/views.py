from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Company, StockDay, Trade
from .serializers import (CompanySerializer, StockDaySerializer,
                          StockPeriodsAnalyticsSerializer,
                          StockPriceAnalyticsSerializer, TradeSerializer)


class CompanyListAPIView(ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class StockDayListAPIView(ListAPIView):
    serializer_class = StockDaySerializer

    def get_queryset(self):
        return StockDay.objects.filter(company__ticker=self.kwargs['ticker'])


class TradeListAPIView(ListAPIView):
    serializer_class = TradeSerializer

    def get_queryset(self):
        return Trade.objects.filter(
            company__ticker=self.kwargs['ticker']
        )


class TradeInsiderListAPIView(TradeListAPIView):

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(insider__slug=self.kwargs.get('insider'))


class BaseStockAnalyticsAPIView(APIView):
    serializer_class = None

    @property
    def company(self):
        return get_object_or_404(Company, ticker=self.kwargs.get('ticker'))

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.query_params)
        if not serializer.is_valid():
            return Response(data={'errors': serializer.errors})

        result = self.calc_analytics(serializer.validated_data)
        return Response(data={'analytics': result})

    def calc_analytics(self, data):
        raise NotImplementedError('Provide logic for analytics.')


class StockPriceAnalyticsAPIView(BaseStockAnalyticsAPIView):
    serializer_class = StockPriceAnalyticsSerializer

    def calc_analytics(self, data):
        """Handle date period from query params and get prices difference.
        """
        prices_qs = StockDay.objects.filter(
            created_date__gte=data['date_from'],
            created_date__lte=data['date_to'],
            company=self.company
        ).order_by('created_date')
        price_start, price_end = prices_qs.first(), prices_qs.last()
        if not price_start or not price_end:
            return Response(data={'diff': {}})

        return price_start.get_prices_diff(price_end)


class StockPeriodsAnalyticsAPIView(BaseStockAnalyticsAPIView):
    serializer_class = StockPeriodsAnalyticsSerializer

    def calc_analytics(self, data):
        """Calculate price periods for company.
        """
        return self.company.get_min_price_periods(
            data['type'], data['value']
        )
