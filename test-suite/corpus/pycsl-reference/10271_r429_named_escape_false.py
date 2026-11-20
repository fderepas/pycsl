r"""Test 10271 -- run #8 u57, route #429 (expected FAIL): the literal spelled with a `\N{GRINNING FACE}` escape (no raw character in the source): `len(x) == 4` (CPython 1). REFUSED: PYCSL-R429-NONLATIN1-STR-LITERAL.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple

#@ ensures \result == 0
#@ assigns \nothing
def f(x: str) -> int:
    if x == "\N{GRINNING FACE}":
        if len(x) == 4:
            return 0
        return 1
    return 0


if __name__ == "__main__":
    r = f("\N{GRINNING FACE}")
    print("VIOLATION contract" if r != 0 else "result", r)
