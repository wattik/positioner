from abc import ABC, abstractmethod

from pymongo import MongoClient
from pymongo.results import InsertOneResult, InsertManyResult

from utils import config
from typing import TypeVar, Generic, Union, Any

T = TypeVar("T")


class BaseMapper(ABC, Generic[T]):
    def __init__(self, collection_name: str, mongo_client: MongoClient):
        self.db_name = config.default("persistence", "db_name")
        self.collection_name = collection_name
        self.collection = mongo_client[self.db_name][self.collection_name]
