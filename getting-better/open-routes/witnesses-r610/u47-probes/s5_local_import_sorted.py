from __future__ import annotations
from typing import Callable, List


#@ ensures len(xs) == \old(len(xs))
def j(xs: List[str]) -> str:
    from os.path import join as sorted
    return ",".join(sorted(xs))
