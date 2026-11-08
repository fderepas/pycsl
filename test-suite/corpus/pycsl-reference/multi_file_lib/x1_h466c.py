"""Helper for corpus 7262 (route #466): a dataclass with a mutable default."""
from dataclasses import dataclass
from typing import List


@dataclass
class P:
    xs: List[int] = []


def g(x: int) -> int:
    return x
