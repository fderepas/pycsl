from typing import Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class P:
    a: int


#@ no_exception \all
def f(k: int) -> int:
    x: Optional[P] = None
    if x is None:
        return 0
    return x.a
