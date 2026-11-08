from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires n == 3
#@ ensures \result == 3
def f(n: int) -> int:
    type n = int
    return n


if __name__ == "__main__":
    try:
        r = f(3)
        if r != 3:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
