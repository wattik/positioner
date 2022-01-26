from collections import Callable, Iterable, defaultdict
from typing import Union

import numpy as np

from positioner.components.option import Option
from positioner.components.order import Order

_MISSING_ = object()


class PandLCache:
    def __init__(self):
        self.cache = defaultdict(dict)

    def _register_many_(self, func, valuable, ins, outs):
        for x, y in zip(ins, outs):
            self.cache[func][(valuable, x)] = y

    def precompute(self, func: Callable, valuables: Union[list, Order, Option], space: Union[np.ndarray, list]):
        if not isinstance(valuables, Iterable):
            valuables = [valuables]

        for valuable in valuables:
            outs = func(valuable, space)
            self._register_many_(func, valuable, space, outs)

        return self.wrap(func)

    def wrap(self, func: Callable):
        values = self.cache[func]

        def wrapper(valuable, x):
            return values.get((valuable, x))

        return wrapper
