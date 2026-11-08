r"""Test 1542 - ROUTE #159 (gen #29): `"abc"[5]` lowered to `str_sub_op s 5 1` (just `""`) with no IndexError obligation and PROVED; CPython raises.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> str:
    s = "abc"
    return s[5]

