from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 1
def g(it: Iterator[int]) -> int:
    y = next(it)
    return 1


#@ ensures \result == 1
def f(it: Iterator[int]) -> int:
    try:
        return g(it)
    except StopIteration:
        return 2


if __name__ == "__main__":
    try:
        r = f(iter([]))
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
