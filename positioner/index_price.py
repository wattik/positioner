import numpy as np
import pandas as pd

def read_index_price_from_order_book(path_to_order_book):
    return np.mean(pd.read_csv(path_to_order_book).indexPrice)