from pymongo import MongoClient
from typing import Any
from persistence.mappers.base_mapper import BaseMapper

# todo use Strategy interface instead of Any


class StrategyMapper(BaseMapper[Any]):
    def __init__(self, mongo_client: MongoClient):
        super().__init__("strategies", mongo_client)