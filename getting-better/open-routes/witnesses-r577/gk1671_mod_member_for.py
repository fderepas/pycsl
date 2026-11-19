from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import enum


class IE(enum.IntEnum):
    A = 1
    B = 2


class EE(enum.Enum):
    A = 1
    B = 2

MA = IE.A


#@ no_exception \all
def f(k: int) -> int:
    t = 0
    for x in MA.value:
        t += 1
    return t


if __name__ == "__main__":
    try:
        print("result", repr(f(1))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
