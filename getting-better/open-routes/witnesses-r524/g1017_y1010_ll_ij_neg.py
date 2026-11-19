from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires 0 <= i and i < len(xss) and 0 <= j and j < len(xss[i])
#@ no_exception \all
def f(xss: List[List[Optional[int]]], i: int, j: int) -> int:
    return -xss[i][j]


if __name__ == "__main__":
    try:
        r = f([[None]], 0, 0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
