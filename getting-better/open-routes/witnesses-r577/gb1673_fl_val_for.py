from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import enum


class IE(enum.IntEnum):
    A = 1
    B = 2



class FL(enum.IntFlag):
    R = 1
    W = 2



@dataclass
class Q:
    m: IE



#@ no_exception \all
def f(k: int, xs: List[int], s: str, ie: IE, q: Q) -> int:
    t = 0
    for x in FL.R.value:
        t += 1
    return t


if __name__ == "__main__":
    try:
        print("result", repr(f(1, [1, 2, 3, 4], "ab", IE.A, Q(IE.A)))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
