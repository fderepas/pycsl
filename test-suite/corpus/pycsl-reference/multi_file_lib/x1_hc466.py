"""Helper for corpus 7285 (route #466 control): a clean module top level."""
from dataclasses import dataclass, field
from typing import List

LIMIT = 10
NAMES = ("a", "b")


@dataclass
class Box:
    xs: List[int] = field(default_factory=list)
    n: int = 0


#@ ensures \result == x + 1
def g(x: int) -> int:
    return x + 1
