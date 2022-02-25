from pymongo import MongoClient

from persistence.mappers.base_mapper import BaseMapper


class OrderbookMapper(BaseMapper):
    def __init__(self, mongo_client: MongoClient):
        super().__init__("orderbooks", mongo_client)
