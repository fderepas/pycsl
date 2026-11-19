r"""Test 1642 - ROUTE #181 control (gen #29): constructing the imported class in a function that neither claims `no_exception` nor catches the exception is unaffected: `C(3).v == 3` proves.
"""
_ = 0  # anchor
from multi_file_lib.r181_raising import C


#@ ensures \result == 3
def probe() -> int:
    c = C(3)
    return c.v
