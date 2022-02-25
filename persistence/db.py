from pymongo import MongoClient
from persistence.mappers.orderbook_mapper import OrderbookMapper
from positioner import config


class Database:
    def __init__(self):
        conn_string = config.default("persistence", "mongo_conn_string")
        self.client = MongoClient(conn_string)


if __name__ == '__main__':
    db = Database()
    om = OrderbookMapper(db.client)
