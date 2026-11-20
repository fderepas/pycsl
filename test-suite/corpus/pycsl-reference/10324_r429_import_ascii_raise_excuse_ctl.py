r"""Test 10324 -- run #8 u59, route #429 review rt71 (expected PASS): over-refusal CONTROL. The main file holds "€" only as a `raise ValueError(..)` message (narrowing 2) and imports an ASCII-only dependency (default "abc"): the excusal still applies across a clean import closure, and the true claim `len(h4()) == 3` proves.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple

from multi_file_lib.r429x_ascii import h4


def boom(n: int) -> int:
    if n < 0:
        raise ValueError("€")
    return n


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    k = h4()
    if len(k) == 3:
        return 0
    return 1


if __name__ == "__main__":
    r = f()
    print("VIOLATION contract" if r != 0 else "result", r)
