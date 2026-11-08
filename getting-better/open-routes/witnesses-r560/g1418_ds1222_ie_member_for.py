from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import enum


class E(enum.Enum):
    A = 1
    B = 2


class IE(enum.IntEnum):
    A = 1



#@ no_exception \all
def f(k: int) -> int:
    c = 0
    for x in IE.A:
        c += 1
    return c


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
