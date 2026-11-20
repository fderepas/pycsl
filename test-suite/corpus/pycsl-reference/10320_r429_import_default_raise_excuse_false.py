r"""Test 10320 -- run #8 u59, route #429 review rt71 (expected FAIL): an imported function whose parameter DEFAULT is "€", called with no argument, while the main file holds the same text only as a `raise ValueError("€")` message: proved `len(h3()) == 3` before (rt71 k05). CPython: len(...) == 1, VIOLATION. REFUSED (PYCSL-R429-NONLATIN1-STR-LITERAL): the narrowing-2 excusal is decided over the whole import closure, so a value a dependency holds is never excused.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple

from multi_file_lib.r429x_default import h3


def boom(n: int) -> int:
    if n < 0:
        raise ValueError("€")
    return n


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    k = h3()
    if len(k) == 3:
        return 0
    return 1


if __name__ == "__main__":
    r = f()
    print("VIOLATION contract" if r != 0 else "result", r)
