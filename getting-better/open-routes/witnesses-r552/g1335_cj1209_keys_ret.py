from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

from rt52dep import g as gi


def h(x: int) -> int:
    return x + 1


@dataclass
class R:
    a: int


#@ no_exception \all
def g2(k: int, xs: List[int], d: Dict[str, int]) -> int:
    return d.keys()


#@ no_exception \all
def f(k: int, xs: List[int], d: Dict[str, int]) -> int:
    return g2(k, xs, d) + 1


if __name__ == "__main__":
    try:
        r = f(1, [1], {"a": 1})
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
