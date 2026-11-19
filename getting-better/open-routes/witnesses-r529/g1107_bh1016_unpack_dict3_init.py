from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, d: Dict[str, int]) -> None:
        a, b = d
        self.k = a


#@ no_exception \all
def f(d: Dict[str, int]) -> int:
    c = C(d)
    return 1


if __name__ == "__main__":
    try:
        r = f({"x": 1, "y": 2, "z": 3})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
