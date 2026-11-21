r"""Test 10272 -- run #8 u57, route #429 (expected FAIL): a MODULE CONSTANT `K = "\u20ac"` compared in the body: `len(x) == 3` (CPython 1). REFUSED: PYCSL-R429-NONLATIN1-STR-LITERAL.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple

K = "\u20ac"


#@ ensures \result == 0
#@ assigns \nothing
def f(x: str) -> int:
    if x == K:
        if len(x) == 3:
            return 0
        return 1
    return 0


if __name__ == "__main__":
    r = f(K)
    print("VIOLATION contract" if r != 0 else "result", r)
