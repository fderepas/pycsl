from typing import Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class P:
    a: int


#@ no_exception \all
def f(k: int) -> int:
    a: List[str] = []
    n = 0
    for p in a:
        n += len(p)
    return n
