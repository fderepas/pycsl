# pycsl-flags: --memory-model hoare
from dataclasses import dataclass
from typing import List


@dataclass
class Point:
    x: int = 0


#@ requires a[0].x == 1
#@ ensures \result == 1
#@ assigns \nothing
def f(a: List[Point]) -> int:
    a[0].x = 5
    return a[0].x
