from django.test import TestCase
from datetime import date

from decimal import Decimal

from ..factories import (CompanyFactory, InsiderFactory, StockDayFactory,
                         TradeFactory)


class TestCompanyModel(TestCase):
    """Tests for `Company` model methods.
    """
    @classmethod
    def setUpTestData(cls):
        cls.company = CompanyFactory()

    def test_get_min_price_periods(self):
        """Ensure that `get_min_price_periods` works correct.

        This method should return all prices with minimal difference greater
        than `min_price`.
        """
        prices_data = [
            (110.0, date(2018, 12, 1)), (112.2, date(2018, 12, 2)),
            (115.7, date(2018, 12, 3)), (109.8, date(2018, 12, 4)),
        ]
        for price, c_date in prices_data:
            StockDayFactory(
                company=self.company, open_price=price, created_date=c_date
            )

        result = self.company.get_min_price_periods('open', 5)
        result_dates = [(obj['date1'], obj['date2']) for obj in result]
        result_prices = [(obj['price1'], obj['price2']) for obj in result]

        self.assertIn(
            (date(2018, 12, 1), date(2018, 12, 3)), result_dates
        )
        self.assertIn(
            (date(2018, 12, 3), date(2018, 12, 4)), result_dates
        )
        self.assertIn((Decimal('110.0'), Decimal('115.7')), result_prices)
        self.assertIn((Decimal('115.7'), Decimal('109.8')), result_prices)


class TestStockDayModel(TestCase):
    """Tests for `StockDay` model methods.
    """
    @classmethod
    def setUpTestData(cls):
        cls.stock_day = StockDayFactory(
            created_date=date(2018, 12, 1),
            open_price=Decimal('110'),
            close_price=Decimal('111'),
            high_price=Decimal('112'),
            low_price=Decimal('113'),
        )

    def test_get_prices_diff(self):
        """Ensure that `get_prices_diff` method returns correct result.
        """
        stock_day2 = StockDayFactory(
            company=self.stock_day.company,
            created_date=date(2018, 12, 6),
            open_price=Decimal('115'),
            close_price=Decimal('116'),
            high_price=Decimal('117'),
            low_price=Decimal('118'),
        )
        result = self.stock_day.get_prices_diff(stock_day2)
        self.assertEqual(
            stock_day2.open_price - self.stock_day.open_price,
            result['open_price']
        )
        self.assertEqual(
            stock_day2.close_price - self.stock_day.close_price,
            result['close_price']
        )
        self.assertEqual(
            stock_day2.high_price - self.stock_day.high_price,
            result['high_price']
        )
        self.assertEqual(
            stock_day2.low_price - self.stock_day.low_price,
            result['low_price']
        )
