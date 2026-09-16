r"""Test 1554 - ROUTE #161 (gen #29): `"{1}".format(0)` lowered to an abstract `val` with no `raises` and PROVED `no_exception IndexError`; CPython raises IndexError. Under a `no_exception` context a call must now reach a program function or a whitelisted builtin/method.
"""
# pycsl-expected: FAIL
from typing import List
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> int:
    s = "{1}".format(0)
    return len(s)

