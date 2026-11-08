from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class P:
    a: int


def h(x: int) -> int:
    return x + 1



#@ no_exception \all
def f(k: int, xs: List[int], s: Set[int], d: Dict[str, int], t: str, b: bytes, p: P) -> int:
    s[0] = 1
    return 1


if __name__ == "__main__":
    try:
        r = f(1, [1, 2], {1, 2}, {"a": 1}, "ab", b"ab", P(1))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
