r"""Test 4326 -- gen #37 route #329 (control, expected PASS): control: `7 if not (x is not None) else 0` on an `Optional[int]` None — a singleton test, still modelled. PROVED.
"""
# pycsl-expected: PASS
from typing import Optional
#@ ensures \result == 7
#@ assigns \nothing
def g() -> int:
    x: Optional[int] = None
    return 7 if not (x is not None) else 0

if __name__ == "__main__":
    assert g() == 7, g()
