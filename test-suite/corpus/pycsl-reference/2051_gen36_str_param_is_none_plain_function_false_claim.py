r"""Test 2051 — gen #36 (expected FAIL): NON-VACUITY twin of 2050 — a `str`-annotated
parameter CAN be `None` at runtime (`tag(None)` returns 2), so `\result == 1` must NOT prove.
"""
# pycsl-expected: FAIL


#@ ensures \result == 1
#@ assigns \nothing
def tag(s: str) -> int:
    if s is not None:
        return 1
    return 2
