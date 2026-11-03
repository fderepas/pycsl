from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    a: int
    s: str


def two() -> int:
    return 2



#@ no_exception \all
def f(k: int) -> int:
    c2 = 0
    for c in k * 2 + 1:
        c2 += 1
    return c2


if __name__ == "__main__":
    try:
        r = f(3)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
