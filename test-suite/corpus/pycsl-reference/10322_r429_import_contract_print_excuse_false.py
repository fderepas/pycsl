r"""Test 10322 -- run #8 u59, route #429 review rt71 (expected FAIL): as 10321, the main-file text being a statement `print("€")` (rt71 h02). CPython: len(...) == 1, VIOLATION. REFUSED (PYCSL-R429-NONLATIN1-STR-LITERAL): the narrowing-2 excusal is decided over the whole import closure, so a value a dependency holds is never excused.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple

from multi_file_lib.r429x_contract import h


def say() -> None:
    print("€")


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    k = h()
    if len(k) == 3:
        return 0
    return 1


if __name__ == "__main__":
    r = f()
    print("VIOLATION contract" if r != 0 else "result", r)
