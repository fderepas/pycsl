from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, xs: List[str]) -> None:
        self.k = sorted(xs, key=lambda x: -x)


#@ no_exception \all
def f(xs: List[str]) -> int:
    c = C(xs)
    return 1


if __name__ == "__main__":
    try:
        r = f(["a", "b"])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
