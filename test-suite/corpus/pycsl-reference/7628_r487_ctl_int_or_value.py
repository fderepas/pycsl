r"""Test 7628 -- route #487 control (expected PASS): `x = n or 5` over ints (the selected int operand, unchanged lowering). PROVED at base 0c61bfc3f and at the repair.
"""
# pycsl-expected: PASS
#@ ensures \result == 5
def f() -> int:
    n = 0
    x = n or 5
    return x
