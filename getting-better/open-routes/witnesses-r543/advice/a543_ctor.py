from typing import Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class P:
    a: int


#@ no_exception \all
def f(k: int) -> int:
    x: P = P(k)
    return x.a
