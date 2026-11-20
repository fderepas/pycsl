r"""Test 10265 -- run #8 u57, route #429 (expected FAIL): rt68 p21: `x == "é"` (combining acute) => `len(x[-1:]) == 2` (CPython 1). REFUSED: PYCSL-R429-NONLATIN1-STR-LITERAL.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple


#@ ensures \result == 0
#@ assigns \nothing
def f(x: str) -> int:
    if x == "é":
        if len(x[-1:]) == 2:
            return 0
        return 1
    return 0


if __name__ == "__main__":
    r = f("é")
    print("VIOLATION contract" if r != 0 else "result", r)
