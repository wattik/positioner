from abc import ABC

from pymongo import MongoClient

from utils import config


class BaseMapper(ABC):
    def __init__(self, collection_name: str, mongo_client: MongoClient):
        self.db_name = config.default("persistence", "db_name")
        self.collection_name = collection_name
        self.collection = mongo_client[self.db_name][self.collection_name]
