from pprint import pprint

from pymongo import MongoClient

from persistence.mappers.strategy_mapper import StrategyMapper
from utils import config

if __name__ == '__main__':
    conn_string = config.default("persistence", "mongo_conn_string")
    client = MongoClient(conn_string)
    sm = StrategyMapper(client)
    pprint(sm.collection.find_one())