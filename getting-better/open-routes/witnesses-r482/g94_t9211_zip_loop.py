from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ \trusted
def k(xs: List[int]) -> int:
    for a, b in zip([xs], [0]):
        a[0] = 7
    return 0


#@ requires len(xs) >= 1 and xs[0] == 0
#@ ensures \result == 0
def f(xs: List[int]) -> int:
    k(xs)
    return xs[0]


if __name__ == "__main__":
    try:
        r = f([0])
        if not (r == 0):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
