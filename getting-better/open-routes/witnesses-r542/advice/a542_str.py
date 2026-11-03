from typing import Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class P:
    a: int


#@ no_exception \all
def f(k: int, s: str) -> int:
    return 1 if "a" in s else 0
