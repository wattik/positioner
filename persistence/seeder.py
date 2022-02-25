from os import listdir
from os.path import isfile, join
from datetime import datetime as dt, timedelta
from persistence.db import Database
from persistence.mappers.orderbook_mapper import OrderbookMapper
from positioner import config
from urllib import request
from ssl import SSLContext
import json
from time import sleep
from positioner.components.option import group_trading_options_by_expiry_date, read_options_from_csv


class CoinAPIClient:
    def __init__(self):
        self.api_key = config.default("coinapi", "api_key")
        self.base_url = config.default("coinapi", "base_url")

    def create_request(self, url: str, append_header=True):
        req = request.Request(url)
        if append_header:
            req.add_header("X-CoinAPI-Key", self.api_key)
        return req

    def get(self, req: request.Request):
        response = request.urlopen(req, context=SSLContext()).read().decode('utf-8')
        return json.loads(response)

    def get_all_symbols(self):
        # https://docs.coinapi.io/#list-all-symbols-get
        url = f"{self.base_url}/v1/symbols?filter_symbol_id=BINANCE_SPOT_"
        req = self.create_request(url)
        return self.get(req)

    def get_historical_price(self, time_start, time_end, symbol_id="BINANCE_SPOT_BTC_USDT", period_id="5MIN", limit=1):
        # https://docs.coinapi.io/#historical-data-get
        url = f"{self.base_url}/v1/ohlcv/{symbol_id}/history?period_id={period_id}&time_start={time_start}&time_end={time_end}&limit={limit}"
        req = self.create_request(url)
        return self.get(req)

    def get_historical_index_price(self, start_time: float, symbol="BTCUSDT", ):
        # BINANCE INSTEAD HERE
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&startTime={start_time}&limit=1"
        req = self.create_request(url, False)
        return self.get(req)


if __name__ == '__main__':
    outputs_path = "./outputs"
    files = [f for f in listdir(outputs_path) if isfile(join(outputs_path, f))]

    db = Database()
    orderbook_mapper = OrderbookMapper(db.client)

    api_client = CoinAPIClient()

    for csv_file in files:
        # parse options and group them
        options = read_options_from_csv(join(outputs_path, csv_file))
        grouped_options = group_trading_options_by_expiry_date(options)

        # parse timestamp from csv filename
        date_format = "%Y-%m-%d-%H-%M-%S"
        str_date = csv_file.split(".")[0]
        start_date = dt.strptime(str_date, date_format)
        start_posix = int(start_date.timestamp()*1000)

        # get index price from the first option or from API if missing
        if "index price" in options[0]:
            index_price = options[0]["index price"]
        else:
            sleep(1)
            data = api_client.get_historical_index_price(start_posix)
            index_price = float(data[0][1])

        # insert order books to mongodb
        order_books = []
        for expiry_date, options in grouped_options.items():
            # print(f"Order book with expiry date {expiry_date} has {len(options)} options. Collected at {start_date}")
            order_book = {
                "option_group": f"BTC-{expiry_date}",
                "options": options,
                "created_at": start_date,
                "index_price": index_price
            }
            order_books.append(order_book)
        insert_result = orderbook_mapper.collection.insert_many(order_books)
        print(f"Inserted {len(insert_result.inserted_ids)} orderbooks")
