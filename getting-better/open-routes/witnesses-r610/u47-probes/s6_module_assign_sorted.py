from __future__ import annotations
from typing import Callable, List


def _kx(xs: List[str]) -> List[str]:
    d = {"a": xs}
    return d["k"]


sorted = _kx


#@ no_exception KeyError
def j(xs: List[str]) -> str:
    return ",".join(sorted(xs))
