r"""Test 10260 -- run #8 u57, route #429 (expected FAIL): rt68 p15: `x == "😀"` => `len(x[:-1]) == 3` PROVED (CPython 0): the literal was modelled as its 4 UTF-8 bytes. REFUSED: PYCSL-R429-NONLATIN1-STR-LITERAL.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple


#@ ensures \result == 0
#@ assigns \nothing
def f(x: str) -> int:
    if x == "😀":
        if len(x[:-1]) == 3:
            return 0
        return 1
    return 0


if __name__ == "__main__":
    r = f("😀")
    print("VIOLATION contract" if r != 0 else "result", r)
