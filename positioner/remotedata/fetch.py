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


def fetch_option_groups(first_group: str, last_group: str, min_expiration_days=20):
    db = Database()
    orderbook_mapper = OrderbookMapper(db.client)

    res = orderbook_mapper.collection.distinct("option_group", {
        "$and": [
            {
                "option_group": {
                    "$lte": last_group
                }
            },
            {
                "option_group": {
                    "$gte": first_group
                }
            }
        ]
    })

    filtered_groups = []
    for group in res:
        first_order_book = orderbook_mapper.collection.find({"option_group": group}).sort("created_at", 1)[0]
        group_time_raw = group.split("-")[1]

        group_timestamp = datetime.strptime(group_time_raw, "%y%m%d")
        expiration_days = abs((group_timestamp - first_order_book["created_at"]).days)
        if expiration_days >= min_expiration_days:
            filtered_groups.append(group)
        # print(f'First order book for {group} with timestamp {group_timestamp} is {first_order_book["created_at"]}. Expires in {expiration_days}')
    return filtered_groups
