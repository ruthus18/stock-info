from django.db import connection, models
from django.template.defaultfilters import slugify
from django.urls import reverse

from .sql_queries import PERIOD_ANALYTICS_SQL


class Company(models.Model):
    """Model for storing company info.

    This is main model which has one-to-many relation with daily stock prices
    and trades (`StockDay` and `Trade`)
    """
    ticker = models.CharField(
        max_length=6,
        unique=True,
    )

    class Meta:
        ordering = ('ticker', )

    def __str__(self):
        return self.ticker

    def get_absolute_url(self):
        return reverse('stocks:company-detail', kwargs={'ticker': self.ticker})

    def get_min_price_periods(self, price_type, min_diff):
        """Get Min periods which difference in price greater than `min_diff`.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                PERIOD_ANALYTICS_SQL.format(
                    type=price_type, min_diff=min_diff,
                    company_id=self.id
                ))
            columns = [col[0] for col in cursor.description]

            return [
                dict(zip(columns, row)) for row in cursor.fetchall()
            ]


class StockDay(models.Model):
    """Model for storing daily prices data for company stock.
    """
    created_date = models.DateField()
    open_price = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0
    )
    close_price = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0
    )
    high_price = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0
    )
    low_price = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0
    )
    volume = models.IntegerField()

    company = models.ForeignKey(
        'stocks.Company',
        on_delete=models.CASCADE,
        related_name='prices'
    )

    class Meta:
        unique_together = ('company', 'created_date', )
        ordering = ('-created_date', )

    def __str__(self):
        return \
            f'({self.created_date}) {self.company.ticker} - {self.close_price}'

    def get_prices_diff(self, end_stock):
        """Get dict with price different between self and `StockDay` instance.
        """
        return {
            'open_price': end_stock.open_price - self.open_price,
            'close_price': end_stock.close_price - self.close_price,
            'high_price': end_stock.high_price - self.high_price,
            'low_price': end_stock.low_price - self.low_price,
        }


class Trade(models.Model):
    """Model for storing info about trades for concrete company stock.
    """
    last_date = models.DateField()
    insider = models.ForeignKey(
        to='stocks.Insider',
        on_delete=models.CASCADE
    )
    relation = models.CharField(
        max_length=32,
        null=True,
        blank=True,
    )
    transaction_type = models.CharField(
        max_length=128,
        null=True,
        blank=True,
    )
    owner_type = models.CharField(
        max_length=32,
        null=True,
        blank=True,
    )
    last_price = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
    )
    traded_shares = models.PositiveIntegerField()
    held_shares = models.PositiveIntegerField()

    company = models.ForeignKey(
        'stocks.Company',
        on_delete=models.CASCADE,
        related_name='trades',
    )

    class Meta:
        ordering = ('-last_date', )

    def __str__(self):
        return f'{self.company.ticker} - {self.insider} ({self.last_date})'


class Insider(models.Model):
    """Model for storing stock insider info.
    """
    name = models.CharField(
        max_length=128,
        unique=True,
    )
    slug = models.SlugField(
        max_length=64
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Populate slug on creation.
        """
        self.slug = slugify(self.name)
        super().save()
