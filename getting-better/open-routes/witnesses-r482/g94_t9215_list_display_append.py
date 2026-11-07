from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ \trusted
def k(xs: List[int]) -> int:
    zs = [xs]
    zs[0].append(7)
    return 0


#@ requires len(xs) == 1
#@ ensures \result == 1
def f(xs: List[int]) -> int:
    k(xs)
    return len(xs)


if __name__ == "__main__":
    try:
        r = f([0])
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
