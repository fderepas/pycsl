r"""Test 10262 -- run #8 u57, route #429 (expected FAIL): rt68 p17: `x == "😀"` => `len(x) == 4` PROVED (CPython 1), pre-existing. REFUSED: PYCSL-R429-NONLATIN1-STR-LITERAL.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple


#@ ensures \result == 0
#@ assigns \nothing
def f(x: str) -> int:
    if x == "😀":
        if len(x) == 4:
            return 0
        return 1
    return 0


if __name__ == "__main__":
    r = f("😀")
    print("VIOLATION contract" if r != 0 else "result", r)
