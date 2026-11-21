from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 0
def g(xs: List[int]) -> int:
    i = xs.index(7)
    return 0


#@ ensures \result == 1
def f(xs: List[int]) -> int:
    try:
        return g(xs) + 1
    except ValueError:
        return 2


if __name__ == "__main__":
    try:
        r = f([1])
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
