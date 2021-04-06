import numpy as np

def space_by_index_price(index_price, delta, n=1000):
    return np.linspace(index_price*(1-delta), index_price*(1+delta), n)