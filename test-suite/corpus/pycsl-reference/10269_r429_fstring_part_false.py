r"""Test 10269 -- run #8 u57, route #429 (expected FAIL): an f-string CONSTANT part above Latin-1 (`f"{n}😀"`), claimed length 5 (CPython 2). REFUSED: PYCSL-R429-NONLATIN1-STR-LITERAL.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple

#@ requires 0 <= n <= 9
#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    s = f"{n}😀"
    if len(s) == 5:
        return 0
    return 1


if __name__ == "__main__":
    r = f(3)
    print("VIOLATION contract" if r != 0 else "result", r)
