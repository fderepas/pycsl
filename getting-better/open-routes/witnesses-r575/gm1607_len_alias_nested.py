from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import os
import os as O
import math
import enum


def h(x: int) -> int:
    return x + 1


class IE(enum.IntEnum):
    A = 1


class EE(enum.Enum):
    A = 1
    S = "ab"

L = len


#@ no_exception \all
def f(k: int, xs: List[int]) -> int:
    return len([y for x in xs for y in L])


if __name__ == "__main__":
    try:
        print("result", repr(f(1, [1, 2]))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
