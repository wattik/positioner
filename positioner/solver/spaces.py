import numpy as np


def space_by_index_price(index_price, delta=None, bounds=None, n=1000):
    if bounds:
        l, u = bounds
    else:
        l, u = index_price * (1 - delta), index_price * (1 + delta)
    return np.linspace(l, u, n)


def clamp_by_rel_bounds(space, center, relative_bounds):
    bounds = (relative_bounds[0] * center, relative_bounds[1] * center)
    return clamp_by_bounds(space, bounds)


def clamp_by_bounds(space, bounds):
    where = (bounds[0] <= space) & (space <= bounds[1])
    return space[where]
