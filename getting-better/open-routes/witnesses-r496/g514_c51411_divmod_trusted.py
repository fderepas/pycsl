from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ \trusted reviewer: rt44
#@ ensures \result == 1
def g(n: int) -> int:
    q, r = divmod(5, n)
    return 1


#@ ensures \result == 1
def f(n: int) -> int:
    try:
        return g(n)
    except ZeroDivisionError:
        return 2


if __name__ == "__main__":
    try:
        r = f(0)
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
