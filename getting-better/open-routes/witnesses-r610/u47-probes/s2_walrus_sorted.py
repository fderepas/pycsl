from __future__ import annotations
from typing import Callable, List


def _app(xs: List[str]) -> List[str]:
    xs.append("q")
    return xs


#@ ensures len(xs) == \old(len(xs))
def j(xs: List[str]) -> str:
    if (sorted := _app):
        pass
    return ",".join(sorted(xs))
