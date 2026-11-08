r"""Test 7431 -- cv6 D1 (expected FAIL, refused): `d.setdefault(k, []).extend(xs)` (the shape of the live Module3_Weaver._parse_extracted_contracts) under `#@ assigns \nothing`. UNEXPECTED PIPELINE ERROR (maximum recursion depth) at base 4d15b89a7: the route #311 probe of the receiver call failed and the node was re-emitted unmarked forever. Now refused by route #280 (`.extend(...)` on a computed receiver). CPython: d gains key k.
"""
# pycsl-expected: FAIL
from typing import Dict, List


#@ requires not (k in d)
#@ ensures \result == 0
#@ assigns \nothing
def f(d: Dict[int, List[int]], k: int, xs: List[int]) -> int:
    d.setdefault(k, []).extend(xs)
    return 1 if k in d else 0


if __name__ == "__main__":
    try:
        r = f({}, 3, [1])
        print("result", r, "VIOLATION" if r != 0 else "")
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
