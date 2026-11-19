from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires n >= 0
#@ ensures \result == 1
def g(n: int) -> int:
    c = chr(n)
    return 1


#@ requires n >= 0
#@ ensures \result == 1
def f(n: int) -> int:
    try:
        return g(n)
    except ValueError:
        return 2


if __name__ == "__main__":
    try:
        r = f(2000000)
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
