from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, xs: List[Any]) -> None:
        self.k = sorted(xs, reverse=True)


#@ no_exception \all
def f(xs: List[Any]) -> int:
    c = C(xs)
    return 1


if __name__ == "__main__":
    try:
        r = f([1, "a"])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
