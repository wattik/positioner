import numpy as np
import pandas as pd

from positioner.components.option import Option


def read_order_book_from_csv(filename, expiry_date=None) -> list[Option]:
    df = pd.read_csv(filename)

    order_book = []
    for i, row in df.iterrows():
        order_book += [Option.make(row.price, row.qnty, row.side, row.symbol)]

    if expiry_date:
        order_book = filter(lambda op: op.expiry == expiry_date, order_book)

    return list(order_book)


def read_order_book_from_dict(data) -> list[Option]:
    order_book = []
    for option in data:
        order_book += [Option.make(option["price"], option["qnty"], option["side"], option["symbol"])]

    return order_book


def read_index_price_from_order_book(path_to_order_book):
    return np.mean(pd.read_csv(path_to_order_book).indexPrice)
