# pycsl-flags: --memory-model hoare
from dataclasses import dataclass
from typing import List


@dataclass
class Point:
    x: int = 0


_ = 0
#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    a: List[Point] = [Point(x=5)]
    return a[0].x
