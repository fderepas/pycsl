"""WL-04g false-twin (int+record) — a MIXED literal [1, Point(2,3)] must NOT prove a
false content claim. Verdict: must NOT be PROVEN."""
_ = 0
from dataclasses import dataclass
from typing import List


@dataclass
class Point:
    x: int
    y: int


#@ ensures \result == 0
def f() -> int:
    a = [1, Point(2, 3)]
    return a[0]
