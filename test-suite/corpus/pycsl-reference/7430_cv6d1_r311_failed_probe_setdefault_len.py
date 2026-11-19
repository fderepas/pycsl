r"""Test 7430 -- cv6 D1 (expected FAIL, refused): `len(d.setdefault(k, []))` under `#@ assigns \nothing`. The route #311 probe of the effectful operand `d.setdefault(k, [])` RAISED (in-place mutator refusal), the node was re-emitted UNMARKED and recursed until Python's stack overflowed: UNEXPECTED PIPELINE ERROR (maximum recursion depth) at base 4d15b89a7. Now the re-emission is marked and the operand's own refusal fires (CPython: setdefault inserts k, f returns 1).
"""
# pycsl-expected: FAIL
from typing import Dict, List


#@ requires not (k in d)
#@ ensures \result == 0
#@ assigns \nothing
def f(d: Dict[int, List[int]], k: int) -> int:
    n = len(d.setdefault(k, []))
    return n + (1 if k in d else 0)


if __name__ == "__main__":
    try:
        r = f({}, 3)
        print("result", r, "VIOLATION" if r != 0 else "")
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
