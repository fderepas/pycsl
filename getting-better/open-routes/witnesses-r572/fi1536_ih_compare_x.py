from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires x == 1824800645
#@ ensures \result == True
#@ assigns \nothing
def f(x: int) -> bool:
    name = x
    name = "abc"
    return name == x


if __name__ == "__main__":
    try:
        r = f(1824800645)
        print("VIOLATION contract" if r is not True else "result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
