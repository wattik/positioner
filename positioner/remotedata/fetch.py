from datetime import datetime

from persistence.db import Database
from persistence.mappers.orderbook_mapper import OrderbookMapper
from positioner.components.option import Option


def fetch_order_books(option_group):
    db = Database()
    orderbook_mapper = OrderbookMapper(db.client)

    def extract_timestamp(raw):
        return raw["created_at"]

    def extract_order_book(raw):
        options_raw = raw["options"]
        order_book = []
        for option_raw in options_raw:
            option = Option.make(
                option_raw["price"], option_raw["qnty"], option_raw["side"], option_raw["symbol"]
            )
            order_book.append(option)

        del options_raw
        return order_book

    def extract_index_price(raw):
        return raw["index_price"]

    timestamps = list(map(
        extract_timestamp,
        orderbook_mapper.collection.find(
            {"option_group": option_group}, {"created_at": 1, "_id": False}
        ).sort(
            "created_at", 1)
    ))

    index_prices = list(map(
        extract_index_price,
        orderbook_mapper.collection.find(
            {"option_group": option_group}, {"index_price": 1, "_id": False}
        ).sort(
            "created_at", 1)
    ))

    order_books = map(
        extract_order_book,
        orderbook_mapper.collection.find(
            {"option_group": option_group}, {"options": 1, "_id": False}
        ).sort(
            "created_at", 1)
    )

    return order_books, index_prices, timestamps


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
        # print(f'First order book for {group} with timestamp {group_timestamp} is {first_order_book["created_at"]}.
        # Expires in {expiration_days}')
    return filtered_groups
