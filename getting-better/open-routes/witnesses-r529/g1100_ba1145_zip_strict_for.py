from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, xs: List[int], ys: List[int]) -> None:
        self.k = 0
        for a, b in zip(xs, ys, strict=True):
            self.k = a


#@ no_exception \all
def f(xs: List[int], ys: List[int]) -> int:
    c = C(xs, ys)
    return 1


if __name__ == "__main__":
    try:
        r = f([1], [])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
