r"""Test 10275 -- run #8 u57, route #429 (expected FAIL): rt68 p20: a lone surrogate literal `"\ud800"` (used to crash the UTF-8 encode): `len(x[:-1]) == 2` (CPython 0). REFUSED: PYCSL-R429-NONLATIN1-STR-LITERAL.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple


#@ ensures \result == 0
#@ assigns \nothing
def f(x: str) -> int:
    if x == "\ud800":
        if len(x[:-1]) == 2:
            return 0
        return 1
    return 0


if __name__ == "__main__":
    r = f("\ud800")
    print("VIOLATION contract" if r != 0 else "result", r)
