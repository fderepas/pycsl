r"""Test 10270 -- run #8 u57, route #429 (expected FAIL): an f-string FORMAT SPEC fill character above Latin-1 (`f"{n:€>3}"`), claimed length != 3 (CPython 3). NOT refused: the literal does not reach the model (no WhyML string literal is emitted for it), so the claim is unconstrained and the file FAILS by proof (default / typed / store), as at base.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple

#@ requires 0 <= n <= 9
#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    s = f"{n:€>3}"
    if len(s) != 3:
        return 0
    return 1


if __name__ == "__main__":
    r = f(3)
    print("VIOLATION contract" if r != 0 else "result", r)
