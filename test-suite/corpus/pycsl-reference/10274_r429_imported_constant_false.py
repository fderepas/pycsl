r"""Test 10274 -- run #8 u57, route #429 (expected FAIL): a str constant IMPORTED from a dependency module (`multi_file_lib/consts429.py: S = "\U0001F600"`): `x == S` => `len(x) == 4` (CPython 1). REFUSED (fail closed).
"""
# pycsl-expected: FAIL
from multi_file_lib.consts429 import S
from typing import Any, Dict, List, Optional, Tuple

#@ ensures \result == 0
#@ assigns \nothing
def f(x: str) -> int:
    if x == S:
        if len(x) == 4:
            return 0
        return 1
    return 0


if __name__ == "__main__":
    r = f(S)
    print("VIOLATION contract" if r != 0 else "result", r)
