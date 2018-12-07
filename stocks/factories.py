import random

import faker
from factory import DjangoModelFactory, SubFactory, lazy_attribute

from . import models

fake = faker.Faker()


class CompanyFactory(DjangoModelFactory):
    """Factory for `Company` model.
    """
    ticker = lazy_attribute(lambda x: fake.word()[:3])

    class Meta:
        model = models.Company


class StockDayFactory(DjangoModelFactory):
    """Factory for `StockDay` model.
    """
    created_date = lazy_attribute(lambda x: fake.date_this_decade())
    volume = random.randint(1000000, 3000000)
    company = SubFactory(CompanyFactory)

    class Meta:
        model = models.StockDay


class InsiderFactory(DjangoModelFactory):
    name = lazy_attribute(lambda x: fake.name_male())

    class Meta:
        model = models.Insider


class TradeFactory(DjangoModelFactory):
    """Factory for `Trade` model.
    """
    insider = SubFactory(InsiderFactory)
    company = SubFactory(CompanyFactory)

    last_date = lazy_attribute(lambda x: fake.date_this_decade())
    traded_shares = random.randint(100, 1000)
    held_shares = random.randint(100, 1000)

    class Meta:
        model = models.Trade
