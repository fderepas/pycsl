from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

from rt52dep import g as gi


class Q:
    def __init__(self) -> None:
        self.a = 1

    def m(self, x: int) -> int:
        return x * 2


#@ no_exception \all
def f(k: int, xs: List[int], d: Dict[str, int], s: str) -> int:
    return gi(sorted(s))


if __name__ == "__main__":
    try:
        r = f(1, [1], {"a": 1}, "a b")
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
