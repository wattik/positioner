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

    groups = om.collection.distinct("option_group", {"option_group": {"$lte": "BTC-210531"}})
    # res = om.collection.distinct("option_group", {"created_at": {"$lte": datetime.fromisoformat("2021-05-31")}})
    print("GROUPS", groups)
