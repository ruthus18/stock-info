from unittest.mock import patch

from django.test import TestCase

from ..models import StockDay, Trade
from ..parsers import NASDAQPriceParser, NASDAQTradeParser


def load_stocks_table(*args, **kwargs):
    """Mock function which uses to mock ``NASDAQStockParser`` parsing.
    """
    return [['11/18/2018', '120.30', '122.1', '132.10', '119.2', '300000']]


def load_trades_table(*args, **kwargs):
    """Mock function which uses to mock ``NASDAQTradeParser`` parsing.
    """
    return [[
        'Jeffrey Leboski', 'Dude', '11/18/2018', 'Incoming',
        'Dude, ok?', '1', '200.0', '1'
    ]]


@patch(
    'stocks.parsers.BaseNASDAQParser.load_table', load_stocks_table
)
class TestNASDAQStockParser(TestCase):
    """Class for testing NASDAQ stock parser.
    """
    def test_price_parser_as_task(self):
        """Ensure that parser can be executing as task.
        """
        parser = NASDAQPriceParser.as_task('abc')

        status = 'Parsed'
        self.assertEqual(parser, status)
        self.assertTrue(
            StockDay.objects.filter(company__ticker='abc').exists()
        )


@patch(
    'stocks.parsers.BaseNASDAQParser.load_table', load_trades_table
)
class TestNASDAQTradeParser(TestCase):
    """Class for testing NASDAQ stock parser.
    """
    def test_trade_parser_as_task(self):
        """Ensure that parser can be executing as task.
        """
        parser = NASDAQTradeParser.as_task('abc')

        status = 'Parsed'
        self.assertEqual(parser, status)
        self.assertTrue(
            Trade.objects.filter(company__ticker='abc').exists()
        )
