r"""Test 7007 -- route #447 (expected FAIL): r3 probe -- `c %= b` (b may be 0: ZeroDivisionError) -- now REFUSED (PYCSL-R447-AUGASSIGN-DIVISION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(a: int, b: int) -> int:
    c = a
    c %= b
    return c
