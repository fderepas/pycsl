from dataclasses import dataclass
from typing import Tuple

@dataclass
class P:
    a: int

#@ requires True
#@ ensures True
def f(x: int) -> Tuple[P, str]:
    return P(x), "pos"
