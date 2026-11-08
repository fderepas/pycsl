r"""Test 7616 -- route #486 control (expected PASS): `s = "a"; s += "b"` (str concatenation on a str local). PROVED at base 0c61bfc3f and at the repair.
"""
# pycsl-expected: PASS
#@ ensures \result == 2
def f() -> int:
    s = "a"
    s += "b"
    return len(s)
