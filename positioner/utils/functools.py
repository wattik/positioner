from collections import Callable, defaultdict
from functools import wraps
from typing import Any, TypeVar, Union

T = TypeVar('T')


def groupby(key: Callable[[T], Any], data: list[T], with_keys=False) -> Union[list[list[T]], list[tuple[Any, list[T]]]]:
    groups_dict = defaultdict(list)
    for d in data:
        groups_dict[key(d)].append(d)

    if with_keys:
        return list(groups_dict.items())
    else:
        return list(groups_dict.values())
