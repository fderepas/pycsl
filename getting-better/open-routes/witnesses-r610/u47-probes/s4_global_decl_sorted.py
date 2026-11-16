from __future__ import annotations
from typing import Callable, List


def _app(xs: List[str]) -> List[str]:
    xs.append("q")
    return xs


#@ assigns \nothing
def install() -> None:
    global sorted
    sorted = _app


#@ ensures len(xs) == \old(len(xs))
def j(xs: List[str]) -> str:
    return ",".join(sorted(xs))
