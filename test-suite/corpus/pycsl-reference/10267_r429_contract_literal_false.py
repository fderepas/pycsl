r"""Test 10267 -- run #8 u57, route #429 (expected FAIL): the non-Latin-1 literal is ONLY in a contract (`#@ requires x == "😀"`): the body proves `len(x) == 4` from it (CPython 1). The emission half refuses it: PYCSL-R429-NONLATIN1-STR-LITERAL.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple

#@ requires x == "😀"
#@ ensures \result == 0
#@ assigns \nothing
def f(x: str) -> int:
    if len(x) == 4:
        return 0
    return 1


if __name__ == "__main__":
    r = f(chr(0x1F600))
    print("VIOLATION contract" if r != 0 else "result", r)
