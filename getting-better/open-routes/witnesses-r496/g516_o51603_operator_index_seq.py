from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 1
def g(xs: List[int]) -> int:
    import operator
    y = operator.indexOf(xs, 3)
    return 1


#@ ensures \result == 1
def f(xs: List[int]) -> int:
    try:
        return g(xs)
    except ValueError:
        return 2


if __name__ == "__main__":
    try:
        r = f([])
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
