from dataclasses import dataclass
from typing import Tuple

@dataclass
class P:
    a: int

#@ requires True
#@ ensures True
def f(x: int) -> Tuple[P, str]:
    if x > 0:
        return P(1), "pos"
    return P(2), "neg"
