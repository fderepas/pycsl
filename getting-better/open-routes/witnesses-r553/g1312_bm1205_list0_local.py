from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires len(xs) >= 1
def g(xs: List[int]) -> None:
    xs[0] = None


#@ no_exception \all
def f(k: int, ys: List[int]) -> int:
    xs = [1]
    g(xs)
    v = xs[0]
    return v + 1


if __name__ == "__main__":
    try:
        r = f(1, [1])
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
