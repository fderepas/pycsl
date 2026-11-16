from __future__ import annotations
from typing import Callable, List


#@ ensures len(xs) == \old(len(xs))
def j(xs: List[str], sorted: Callable[[List[str]], List[str]]) -> str:
    return ",".join(sorted(xs))
