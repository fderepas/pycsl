from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    a: int
    s: str


def two() -> int:
    return 2



#@ no_exception \all
def f(b: bool) -> int:
    return sum(1 for c in b)


if __name__ == "__main__":
    try:
        r = f(True)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
