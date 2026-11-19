from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires len(xs) >= 1
def g(xs: List[int]) -> None:
    xs[0] = None


#@ no_exception \all
def f(k: int) -> int:
    xs = [1]
    g(xs)
    n = 0
    for i in range(xs[0]):
        n += 1
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
