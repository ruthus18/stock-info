import logging
from concurrent import futures
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

from .models import Company, StockDay, Trade, Insider

__all__ = ('parse_nasdaq_data', )

logger = logging.getLogger(__name__)


def parse_date(value):
    if ':' in value:
        return date.today()

    return datetime.strptime(value, '%m/%d/%Y').date()


def parse_int(value):
    return value.replace(',', '')


class BaseNASDAQParser:
    """Base parser class for data from NASDAQ.

    Provide main logic for grabbing and parsing data. Also has an interface
    for using as async tasks (`BaseNASDAQAParser.as_task` classmethod).
    After parsing, check `Company` model and save instances in DB in bulk.
    """
    base_url = 'http://www.nasdaq.com/symbol/'
    model = None
    fields = ()
    identify_args = ()
    paginated = True

    def __init__(self, ticker):
        self.ticker = ticker.lower()

    def load_table(self, related_url, page=None, handle_pagination=True):
        """Build URL for parsing, load HTML page and extract table with data.

        Returns:
            list - array of rows with price day data.
        """
        url = self.base_url + related_url
        params = {'page': page} if page else None

        html = requests.get(url, params=params).content
        soup = BeautifulSoup(html, 'html.parser')
        rows = self.parse_table(soup)

        if handle_pagination:
            # Load other pages and append to main table
            last_page = self.parse_last_page(soup)

            # Page pages from 2 to last_page (but <= 10)
            for pag_page in range(2, min(11, last_page + 1)):
                pag_rows = self.load_table(
                    related_url, page=pag_page, handle_pagination=False
                )
                rows += pag_rows

        return rows[1:] if '\n' not in rows[1] else rows[2:]

    def parse_table(self, soup):
        """Convert HTML table to 2-dimensional list.
        """
        raw_table = soup.find('div', attrs={'class': 'genTable'})

        if not raw_table:
            return []

        return [
            [elem.text for elem in row.find_all('td')]
            for row in raw_table.find_all('tr')
        ]

    def parse_last_page(self, soup):
        """Parse number of last page which used in pagination.
        """
        last_page_link = soup.find('a', attrs={
            'id': 'quotes_content_left_lb_LastPage'}
        ).attrs.get('href')

        if last_page_link:
            return int(last_page_link.strip('page=')[-1])

    def clean_value(self, value):
        """Clean HTML table value from NASDAQ page.
        """
        return value.replace('\r\n', '').strip()

    def convert_obj_values(self, obj):
        """Base method which used for custom data cleaning.
        """
        return obj

    def import_data(self):
        """Get instance data of models, create instances in bulk.

        On creation, method check by `identify_args` already existed
        instances in database and pop from instance dict.
        """
        existed_qs = self.model.objects \
            .filter(company=self.company) \
            .values_list(*self.identify_args)

        self.model.objects.bulk_create([
            self.model(company=self.company, **instance_data)
            for instance_data in self.data
            if tuple([
                instance_data[arg] for arg in self.identify_args
            ]) not in existed_qs
        ])

    def process_parsing(self):
        """Main function for parsing data.

        Load data from NASDAQ site, clean and validate and save in transaction.
        """
        raw_table = self.load_table(
            self.url, handle_pagination=self.paginated
        )
        # Clean values and convert to list of dicts
        self.data = [dict(zip(
            self.fields, [self.clean_value(value) for value in row]
        )) for row in raw_table]

        if not self.data:
            self.status = 'Not Found'
            return

        for obj in self.data:
            obj = self.convert_obj_values(obj)

        self.import_data()
        self.status = 'Parsed'

    @property
    def company(self):
        company, _ = Company.objects.get_or_create(ticker=self.ticker)
        return company

    @property
    def url(self):
        raise NotImplementedError(
            'You should define the related URL for parsing'
        )

    @classmethod
    def as_task(cls, ticker):
        """Get parser class as task.

        By call `BaseNASDAQParser.as_task(ticker)` we can initiate and run
        parser which is cose to use in concurrent workers
        such as `ProcessPoolExecutor`.
        """
        instance = cls(ticker)
        instance.process_parsing()
        return instance.status


class NASDAQPriceParser(BaseNASDAQParser):
    """Parser class for handling page with historical stock prices.

    Parse `historical` page for concrete company ticker and load data
    into `StockDay` model.
    """
    model = StockDay
    fields = (
        'created_date', 'open_price', 'high_price',
        'low_price', 'close_price', 'volume',
    )
    identify_args = ('created_date', )
    paginated = False

    @property
    def url(self):
        return f'{self.ticker}/historical'

    def convert_obj_values(self, obj):
        obj['volume'] = parse_int(obj['volume'])
        obj['created_date'] = parse_date(obj['created_date'])

        return obj


class NASDAQTradeParser(BaseNASDAQParser):
    """Parser class for handling page with insider trade.

    Parse `insider-trades` page for concrete company ticker and load data
    into `Insider` and `Trade` models.
    """
    model = Trade
    fields = (
        'insider', 'relation', 'last_date', 'transaction_type',
        'owner_type', 'traded_shares', 'last_price', 'held_shares',
    )
    identify_args = (
        'insider', 'relation', 'last_date', 'transaction_type', 
        'traded_shares'
    )

    @property
    def url(self):
        return f'{self.ticker}/insider-trades'

    def convert_obj_values(self, obj):
        obj['traded_shares'] = parse_int(obj['traded_shares'])
        obj['held_shares'] = parse_int(obj['held_shares'])
        obj['last_date'] = parse_date(obj['last_date'])
        obj['insider'], _ = Insider.objects.get_or_create(name=obj['insider'])

        if not obj['last_price']:
            obj.pop('last_price')

        return obj


def parse_nasdaq_data(tickers_list, max_workers=None):
    """
    Main function for grabbing data about stock prices and trades from
    NASDAQ site.
    """
    with futures.ProcessPoolExecutor(max_workers) as executor:
        price_futures = executor.map(
            NASDAQPriceParser.as_task, tickers_list
        )
        trade_futures = executor.map(
            NASDAQTradeParser.as_task, tickers_list
        )

        logger.info('Parsing stock prices...')
        for ticker, status in zip(tickers_list, price_futures):
            logger.info(f'{ticker.upper()} - {status}')

        logger.info('Parsing trades...')
        for ticker, status in zip(tickers_list, trade_futures):
            logger.info(f'{ticker.upper()} - {status}')

        logger.info('------\nDone.')
