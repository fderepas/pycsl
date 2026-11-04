from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires len(xs) >= 1
def g(xs: List[int]) -> None:
    xs[0] = None


def h(x: int) -> int:
    return x + 1


#@ no_exception \all
def f(k: int) -> int:
    xs = [1]
    g(xs)
    return h(xs[0])


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
