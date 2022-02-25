from collections import Callable, Iterable, defaultdict
from typing import Union

import numpy as np

from positioner.components.option import Option
from positioner.components.order import Order

_MISSING_ = object()


class PandLCache:
    def __init__(self):
        self.cache = defaultdict(lambda: defaultdict(dict))

    def _register_many_(self, func, valuable, ins, outs):
        d = self.cache[func][valuable]
        for x, y in zip(ins, outs):
            d[x] = y

    def precompute(self, func: Callable, valuables: Union[Iterable, Order, Option], space: Union[np.ndarray, list]):
        if not isinstance(valuables, Iterable):
            valuables = [valuables]

        for valuable in valuables:
            outs = func(valuable, space)
            self._register_many_(func, valuable, space, outs)

        return self.wrap(func)

    def wrap(self, func: Callable):
        d = self.cache[func]

        def wrapper(valuable, x):
            return d[valuable][x]

        return wrapper
