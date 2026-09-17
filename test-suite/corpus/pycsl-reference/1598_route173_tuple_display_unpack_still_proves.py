r"""Test 1598 - ROUTE #173 control (gen #29): unpacking a tuple display of the target count under `#@ no_exception ValueError` still proves.
"""
_ = 0  # anchor


#@ no_exception ValueError
#@ ensures \result == 3
def probe() -> int:
    a, b = 1, 2
    return a + b
