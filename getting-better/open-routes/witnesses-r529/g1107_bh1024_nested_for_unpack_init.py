from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, xs: List[Tuple[int, int]]) -> None:
        self.k = 0
        for (a, b), c in xs:
            self.k = a


#@ no_exception \all
def f(xs: List[Tuple[int, int]]) -> int:
    c = C(xs)
    return 1


if __name__ == "__main__":
    try:
        r = f([(1, 2)])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
