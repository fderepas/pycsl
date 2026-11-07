r"""Advice probe for route #471 (move the class to module level, `field(default_factory=list)`), from test 7364 -- route #471 (expected FAIL): red-team 38 witness `g13_k145_realistic_local_record` -- a local `@dataclass` with a mutable list default (ValueError). PROVED at base a9eac4a08 / daf5c3d1f under `#@ no_exception \all`; now REFUSED (PYCSL-R471-LOCAL-CLASS-RAISES).
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass, field


@dataclass
class Acc:
    items: List[int] = field(default_factory=list)
    total: int = 0

#@ no_exception \all
def f(n: int) -> int:
    a = Acc()
    return a.total + n


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
