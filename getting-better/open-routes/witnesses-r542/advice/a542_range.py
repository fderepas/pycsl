from typing import Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class P:
    a: int


#@ no_exception \all
def f(k: int) -> int:
    c2 = 0
    for c in range(k):
        c2 += 1
    return c2
