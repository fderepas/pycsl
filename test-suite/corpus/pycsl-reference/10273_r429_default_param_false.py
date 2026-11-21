r"""Test 10273 -- run #8 u57, route #429 (expected FAIL): a parameter DEFAULT `y: str = "\u20ac"`: `x == y` => `len(x) == 3` (CPython 1). NOT refused: the literal does not reach the model (no WhyML string literal is emitted for it), so the claim is unconstrained and the file FAILS by proof (default / typed / store), as at base.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple

#@ ensures \result == 0
#@ assigns \nothing
def f(x: str, y: str = "\u20ac") -> int:
    if x == y:
        if len(x) == 3:
            return 0
        return 1
    return 0


if __name__ == "__main__":
    r = f("\u20ac")
    print("VIOLATION contract" if r != 0 else "result", r)
