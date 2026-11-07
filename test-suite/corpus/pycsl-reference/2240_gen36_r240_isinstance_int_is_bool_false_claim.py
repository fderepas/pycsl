r"""Test 2240 — route #240 (expected FAIL): `isinstance(<int>, bool)` was DECIDED TRUE. Decision A
collapses `bool` onto `tag_int`, so for `x: int` the test lowered to `(0 = 0)` and `\result == 1`
PROVED at 1e4b380e while CPython `f(5)` = 0 (an int is not a bool; only the converse holds). The
model cannot tell `True` from `1`, so the test is now UNDECIDED (the receiver-carrying
`py_isinstance_bool_int_op x`, a fresh result per evaluation) and the postcondition is unproved.
Controls: 2250, 2251.
"""
# pycsl-expected: FAIL


#@ ensures \result == 1
#@ assigns \nothing
def f(x: int) -> int:
    if isinstance(x, bool):
        return 1
    return 0
