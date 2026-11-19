from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, xs: List[int], ys: List[int], zs: List[int]) -> None:
        self.k = list(zip(xs, ys, zs, strict=True))


#@ no_exception \all
def f(xs: List[int], ys: List[int], zs: List[int]) -> int:
    c = C(xs, ys, zs)
    return 1


if __name__ == "__main__":
    try:
        r = f([1], [1], [])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
