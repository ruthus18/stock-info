from django.core.management.base import BaseCommand

from ...parsers import parse_nasdaq_data


class Command(BaseCommand):
    help = 'Parse stocks data from NASDAQ site'

    def add_arguments(self, parser):
        parser.add_argument(
            'path', type=str, help='Path to file with tickers list'
        )
        parser.add_argument(
            '--max-workers', type=int, help='Max num of workers'
        )

    def handle(self, *args, **kwargs):
        path = kwargs.get('path')
        max_workers = kwargs.get('max_workers')

        with open(path, 'r') as tickers_file:
            tickers = [
                ticker.lower().strip()
                for ticker in tickers_file.readlines()
            ]

        parse_nasdaq_data(tickers, max_workers=max_workers)
