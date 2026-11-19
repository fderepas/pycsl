from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import enum
import math
import os
import functools
class IE(enum.IntEnum):
    A = 1
    B = 2
class FL(enum.IntFlag):
    R = 1
    W = 2
class SE(enum.StrEnum):
    S = "ab"
class KI:
    def __init__(self, a: int) -> None:
        self.a = a
@dataclass
class P:
    a: int
def h(x: int) -> int:
    return x + 1

#@ no_exception \all
def f(k: int, xs: List[int], s: str, ki: KI) -> int:
    return 1 if k in IE.A.name else 0


if __name__ == "__main__":
    try:
        print("result", repr(f(1, [1, 2], "ab", KI(1)))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
