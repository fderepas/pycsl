from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class C:
    def __init__(self) -> None:
        self.v = 0
        self.xs: List[int] = [0]


#@ \trusted
def k(d: Dict[int, int]) -> int:
    e = (d,)[0]
    e[1] = 7
    return 0


#@ requires 1 in d and d[1] == 0
#@ ensures \result == 0
def f(d: Dict[int, int]) -> int:
    k(d)
    return d[1]


if __name__ == "__main__":
    try:
        r = f({1: 0})
        if not (r == 0):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
