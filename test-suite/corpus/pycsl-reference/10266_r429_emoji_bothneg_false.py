r"""Test 10266 -- run #8 u57, route #429 (expected FAIL): rt68 p22: `x == "a😀"` => `x[-2:-1] == "a" and len(x[-3:]) == 3` (CPython False). REFUSED: PYCSL-R429-NONLATIN1-STR-LITERAL.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple


#@ ensures \result == 0
#@ assigns \nothing
def f(x: str) -> int:
    if x == "a😀":
        if x[-2:-1] == "a" and len(x[-3:]) == 3:
            return 0
        return 1
    return 0


if __name__ == "__main__":
    r = f("a😀")
    print("VIOLATION contract" if r != 0 else "result", r)
