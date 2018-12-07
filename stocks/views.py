from django.views.generic import DetailView, ListView

from .models import Company, Insider, StockDay, Trade


class CompanyListView(ListView):
    """View for displaying companies list.
    """
    model = Company
    template_name = 'companies_list.html'


class CompanyDetailView(DetailView):
    """View for displaying prices for concrete stock.
    """
    model = Company
    slug_field = 'ticker'
    slug_url_kwarg = 'ticker'
    template_name = 'company_detail.html'


class TradeListView(ListView):
    """Base view for displaying stock insiders trades.
    """
    model = Trade
    template_name = 'trades_list.html'

    @property
    def company(self):
        return Company.objects.get(ticker=self.kwargs.get('ticker'))

    def get_queryset(self):
        return self.model.objects.filter(company=self.company)

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['company'] = self.company
        return ctx


class TradeInsiderListView(TradeListView):
    """View for displaying trades for concrete stock and insider.
    """
    template_name = 'trades_insider_list.html'

    @property
    def insider(self):
        return Insider.objects.get(slug=self.kwargs.get('insider'))

    def get_queryset(self):
        """Filter parent qs by selected insider.
        """
        qs = super().get_queryset()
        return qs.filter(insider=self.insider)

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['insider'] = self.insider
        return ctx


class BaseAnalyticsView(CompanyDetailView):
    """Base view for stocks analytics.

    Provide company handling and base skeleton for analytics logic.
    """

    def calc_analytics(self):
        raise NotImplementedError(
            'You should provide logic for analytics calculation'
        )

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)

        analytics_dict = self.calc_analytics()
        ctx.update({
            'msg': getattr(self, 'msg', ''),
            'analytics': analytics_dict
        })
        return ctx


class StockPriceAnalyticsView(BaseAnalyticsView):
    template_name = 'stock_analytics.html'

    def calc_analytics(self):
        """Handle date period from query params and get prices difference.
        """
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        if not date_from or not date_to:
            self.msg = (
                'You should to specify `date_from` and `date_to` '
                'query params'
            )
            return

        prices_qs = StockDay.objects.filter(
            created_date__gte=date_from, created_date__lte=date_to,
            company=self.object
        ).order_by('created_date')
        price_start, price_end = prices_qs.first(), prices_qs.last()

        if not price_start or not price_end:
            self.msg = \
                'Not enough data about stock prices for selected period.'
            return

        self.msg = f'Price difference between {date_from} - {date_to}'

        prices_diff = price_start.get_prices_diff(price_end)
        prices_diff.update({
            'start_obj': price_start,
            'end_obj': price_end
        })
        return prices_diff


class StockPeriodsAnalyticsView(BaseAnalyticsView):
    template_name = 'stock_periods.html'
    price_types = ('open', 'high', 'low', 'close')

    def calc_analytics(self):
        """Calculate price periods for company.
        """
        price_type = self.request.GET.get('type')
        min_diff = self.request.GET.get('value')

        if not price_type or not min_diff:
            self.msg = (
                'You should specify `type` and `value` params.'
            )
            return

        if price_type not in self.price_types:
            self.msg = (
                f'Wrong price type: "{price_type}", available types are '
                f'{self.price_types}'
            )
            return
        try:
            int(min_diff)
        except ValueError:
            self.msg = '`value` should be an integer number.'
            return

        self.msg = (
            f'Price periods with {price_type} price '
            f'difference greater than {min_diff}'
        )
        return {
            'periods': self.object.get_min_price_periods(price_type, min_diff),
            'price_type': price_type
        }
