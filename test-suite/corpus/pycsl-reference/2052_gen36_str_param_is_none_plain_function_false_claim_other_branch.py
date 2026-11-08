r"""Test 2052 — gen #36 (expected FAIL): the OTHER branch of 2050 — `tag("a")` returns 1,
so `\result == 2` must NOT prove either (the sentinel decides nothing).
"""
# pycsl-expected: FAIL


#@ ensures \result == 2
#@ assigns \nothing
def tag(s: str) -> int:
    if s is not None:
        return 1
    return 2
