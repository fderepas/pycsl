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
def f(k: int, e: EE, q: Q) -> int:
    return sum(1 for x in e.value)


if __name__ == "__main__":
    try:
        print("result", repr(f(1, EE.A, Q(EE.A)))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
