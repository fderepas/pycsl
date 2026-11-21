from __future__ import annotations
from typing import Callable, List


def _kx(xs: List[str]) -> List[str]:
    d = {"a": xs}
    return d["k"]


class O:
    class I:
        #@ no_exception KeyError
        def j(self, xs: List[str], sorted: Callable[[List[str]], List[str]]) -> str:
            return ",".join(sorted(xs))
