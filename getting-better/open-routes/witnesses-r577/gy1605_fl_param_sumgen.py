from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import enum


class EE(enum.Enum):
    A = 1
    S = "ab"


class FL(enum.IntFlag):
    R = 1


@dataclass
class Q:
    e: EE


#@ no_exception \all
def f(k: int, fl: FL, q: Q) -> int:
    return sum(1 for x in fl.value)


if __name__ == "__main__":
    try:
        print("result", repr(f(1, FL.R, Q(EE.A)))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
