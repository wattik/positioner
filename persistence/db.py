from pymongo import MongoClient
from persistence.mappers.orderbook_mapper import OrderbookMapper
from positioner import config
from datetime import datetime


class Database:
    def __init__(self):
        conn_string = config.default("persistence", "mongo_conn_string")
        self.client = MongoClient(conn_string)


if __name__ == '__main__':
    db = Database()
    om = OrderbookMapper(db.client)

    res = om.collection.distinct("option_group", {"option_group": {"$lte": "BTC-210531"}})
    # res = om.collection.distinct("option_group", {"created_at": {"$lte": datetime.fromisoformat("2021-05-31")}})

    for group in res:
        first_order_book = om.collection.find({"option_group": group}).sort("created_at", 1)[0]
        group_time_raw = group.split("-")[1]

        group_timestamp = datetime.strptime(group_time_raw, "%y%m%d")
        expiration_days = abs((group_timestamp - first_order_book["created_at"]).days)
        print(f'First order book for {group} with timestamp {group_timestamp} is {first_order_book["created_at"]}. Expires in {expiration_days}')
    # print(res)

def