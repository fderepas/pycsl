from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, t: Tuple[int, int, int]) -> None:
        a, b = t
        self.k = a


#@ no_exception \all
def f(t: Tuple[int, int, int]) -> int:
    c = C(t)
    return 1


if __name__ == "__main__":
    try:
        r = f((1, 2, 3))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
