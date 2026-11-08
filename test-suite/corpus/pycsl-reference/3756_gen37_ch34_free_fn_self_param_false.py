r"""Test 3756 -- gen #37 ch34 (expected FAIL): false twin of 3755: `succ(3)` is 4 in CPython (the free function's `self` parameter is an ordinary argument), so claiming 3 must NOT prove.
"""
# pycsl-expected: FAIL


def succ(self: int) -> int:
    return self + 1


#@ ensures \result == 3
#@ assigns \nothing
def use_succ() -> int:
    return succ(3)
