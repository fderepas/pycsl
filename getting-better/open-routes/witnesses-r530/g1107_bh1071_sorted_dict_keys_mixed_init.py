from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, d: Dict[Any, int]) -> None:
        self.k = sorted(d)


#@ no_exception \all
def f(d: Dict[Any, int]) -> int:
    c = C(d)
    return 1


if __name__ == "__main__":
    try:
        r = f({1: 1, "a": 2})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
