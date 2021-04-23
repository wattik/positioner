from pymongo import MongoClient

from persistence.mappers.base_mapper import BaseMapper


class StrategyMapper(BaseMapper):
    def __init__(self, mongo_client: MongoClient):
        super().__init__("strategies", mongo_client)