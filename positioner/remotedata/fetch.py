from datetime import datetime

from persistence.db import Database
from persistence.mappers.orderbook_mapper import OrderbookMapper
from positioner.components.option import Option


def fetch_order_books(option_group):
    db = Database()
    orderbook_mapper = OrderbookMapper(db.client)
    cur = orderbook_mapper.collection.find({"option_group": option_group})

    order_books = []
    prices = []
    timestamps = []
    for orderbook_raw in cur:
        options_raw = orderbook_raw["options"]
        price = orderbook_raw["index_price"]
        ts = orderbook_raw["created_at"]

        order_book = []
        for option_raw in options_raw:
            option = Option.make(option_raw["price"], option_raw["qnty"], option_raw["side"], option_raw["symbol"])
            order_book.append(option)

        order_books.append(order_book)
        prices.append(price)
        timestamps.append(ts)

    return order_books, prices, timestamps


def fetch_option_groups(last_group: str):
    db = Database()
    orderbook_mapper = OrderbookMapper(db.client)
    return orderbook_mapper.collection.distinct("option_group", {"option_group": {"$lte": last_group}})
