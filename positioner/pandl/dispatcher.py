from functools import cached_property, lru_cache
from typing import Callable, Union

import numpy as np

from positioner.components.option import Option, OptionType, Side
from positioner.components.order import Order
from positioner.pandl.utils import ArrayOrNumber, dispatch_non_arrays


class EvaluationFuncDispatcher:
    def __init__(self, option_type_funcs: dict[str, Callable]):
        self.funcs = option_type_funcs

    @cached_property
    def buy_call(self):
        return dispatch_non_arrays(1)(self.funcs["buy_call"])

    @cached_property
    def sell_call(self):
        return dispatch_non_arrays(1)(self.funcs["sell_call"])

    @cached_property
    def buy_put(self):
        return dispatch_non_arrays(1)(self.funcs["buy_put"])

    @cached_property
    def sell_put(self):
        return dispatch_non_arrays(1)(self.funcs["sell_put"])

    def _dispatch_list_(self, to_be_valued: list[Union[Option, Order]], space: ArrayOrNumber):
        if len(to_be_valued) == 0:
            return np.zeros_like(space)

        # non-empty list
        if isinstance(to_be_valued[0], Order):
            return sum(self._dispatch_order_(o, space) for o in to_be_valued)
        if isinstance(to_be_valued[0], Option):
            return sum(self._dispatch_option_(o, space) for o in to_be_valued)

        raise ValueError(to_be_valued)

    def _dispatch_option_(self, to_be_valued: Option, space: ArrayOrNumber):
        if to_be_valued.option_type == OptionType.CALL:
            if to_be_valued.side == Side.ASK:
                return self.buy_call(to_be_valued, space)
            else:
                return self.sell_call(to_be_valued, space)
        if to_be_valued.option_type == OptionType.PUT:
            if to_be_valued.side == Side.ASK:
                return self.buy_put(to_be_valued, space)
            else:
                return self.sell_put(to_be_valued, space)

        raise ValueError(to_be_valued)

    def _dispatch_order_(self, to_be_valued: Order, space: ArrayOrNumber):
        return to_be_valued.quantity * self._dispatch_option_(to_be_valued.option, space)

    def __call__(self, to_be_valued: Union[Option, Order, list], space: ArrayOrNumber):
        if isinstance(to_be_valued, Order):
            return self._dispatch_order_(to_be_valued, space)

        if isinstance(to_be_valued, Option):
            return self._dispatch_option_(to_be_valued, space)

        if isinstance(to_be_valued, list):
            return self._dispatch_list_(to_be_valued, space)

        raise ValueError(to_be_valued)
