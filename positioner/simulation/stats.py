import pandas as pd
from namespaces import Namespace

from positioner.components.order import Order
from positioner.pandl import value, exercise_fee, order_margin, future_expenses


class Recorder:
    def __init__(self):
        self.__history__: list[dict] = []

    def empty(self):
        return len(self.__history__) == 0

    @property
    def last(self):
        return Namespace(self.__history__[-1])

    def add_result(self, **items):
        self.__history__.append(items)

    def __getitem__(self, item):
        return [d[item] for d in self.__history__]

    def apply(self, f):
        self.__history__ = [(d | f(**d)) for d in self.__history__]

    def to_df(self):
        return pd.DataFrame(self.__history__)

    def __iter__(self):
        return iter(self.__history__)


class StatsComputer:
    def __init__(self, final_index_price: float):
        self.final_index_price = final_index_price

    @staticmethod
    def add_pandl(d: dict, index_price, position, account, total_budget, prefix=""):
        d[prefix + "_value"] = value(position, index_price)
        d[prefix + "_order_margin"] = order_margin(position, index_price)
        d[prefix + "_exercise_fee"] = exercise_fee(position, index_price)
        d[prefix + "_future_expenses"] = future_expenses(position, index_price)
        d[prefix + "_pandl"] = account + d[prefix + "_value"] - d[prefix + "_exercise_fee"] - total_budget

    def __call__(
        self,
        position: list[Order],
        index_price: float,
        account: float,
        total_budget: float,
        **other_fields
    ) -> dict:
        d = dict()
        self.add_pandl(d, index_price, position, account, total_budget, prefix="current")
        self.add_pandl(d, self.final_index_price, position, account, total_budget, prefix="final")
        return d
