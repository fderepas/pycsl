from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    a: int
    s: str


def two() -> int:
    return 2



#@ no_exception \all
def f(t: Tuple[int, str]) -> int:
    return 1 if 1 in t[0] else 0


if __name__ == "__main__":
    try:
        r = f((3, "x"))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
