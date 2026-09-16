r"""Test 1529 - ROUTE #156 (gen #29): the same nesting with the outer handler doing `x = x + 1`; `\result != 8` PROVED; CPython 8.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result != 8
def probe() -> int:
    x = 0
    try:
        try:
            raise ValueError
        finally:
            x = 7
    except ValueError:
        x = x + 1
    return x

