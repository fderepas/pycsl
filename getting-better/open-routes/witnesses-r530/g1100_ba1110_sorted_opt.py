from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, xs: List[Optional[int]]) -> None:
        self.k = sorted(xs)


#@ no_exception \all
def f(xs: List[Optional[int]]) -> int:
    c = C(xs)
    return 1


if __name__ == "__main__":
    try:
        r = f([1, None])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
