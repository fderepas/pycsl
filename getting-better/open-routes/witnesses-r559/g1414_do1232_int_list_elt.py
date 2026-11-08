from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import math


def h(x: int) -> int:
    return x + 1


@dataclass
class R:
    a: int



#@ no_exception \all
def f(k: int, xs: List[int]) -> int:
    ys = [int]
    return ys[0] + 1


if __name__ == "__main__":
    try:
        r = f(1, [1, 2])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
