# pycsl-flags: --memory-model hoare
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Point:
    x: int = 0


_ = 0
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    kw: Dict[str, int] = {"x": 5}
    a: List[Point] = [Point(**kw)]
    return a[0].x
