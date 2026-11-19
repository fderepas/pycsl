from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, s: Set[int]) -> None:
        a, b = s
        self.k = a


#@ no_exception \all
def f(s: Set[int]) -> int:
    c = C(s)
    return 1


if __name__ == "__main__":
    try:
        r = f({1})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
