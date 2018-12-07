# Stock Info

Приложение для парсинга стоимости акций и сделок акционеров с сайта NASDAQ

* http://www.nasdaq.com/symbol/cvx/historical
* http://www.nasdaq.com/symbol/cvx/insider-trades

### API ссылки:

* /api/ - список тикеров акций
* /api/{ ticker }/ - список цен акции компании
* /api/{ ticker }/insider/ - список сделок
* /api/{ ticker }/insider/{ name }/ - список сделок для конкретного акционера
* /api/{ ticker }/analytics/?date_from=..&date_to=.. - разница цены акции за выбранный период
* /api/{ ticker }/delta/?type=..&value=.. - список отрезков цен с выбранным изменением и типом цены

### Требования:

* Python 3.6
* PostgreSQL 10

### Как запустить:

1. Создать .env файл с настройками проектв и БД (пример файла в .env.example)
2. `pip install -r requirements.txt`
3. `python manage.py migrate`

### Как спарсить данные с сайта:

1. Создать файл с тикерами акций (пример файла в tickers.txt)
2. Выполнить `python manage.py parse_stocks tickers.txt --max-workers 10`

