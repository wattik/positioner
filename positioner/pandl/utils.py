from numbers import Number
from typing import NewType, Union, Callable

import numpy as np


def ndarray_argument_convertor(f, pos, *args, **kwargs):
    if isinstance(args[pos], Number):
        new_args = list(args)
        new_args[pos] = np.asarray([new_args[pos]])
        return float(f(*new_args, **kwargs)[0])

    elif isinstance(args[pos], list):
        new_args = list(args)
        new_args[pos] = np.asarray(new_args[pos])
        return f(*new_args, **kwargs)

    return f(*args, **kwargs)


def dispatch_non_arrays(pos) -> Callable:
    def annotation(f) -> Callable:
        def wrapper(*args, **kwargs):
            return ndarray_argument_convertor(f, pos, *args, **kwargs)

        return wrapper

    return annotation


ArrayOrNumber = NewType("ArrayOrNumber", Union[np.ndarray, Number])
