r"""Test 7006 -- route #447 (expected FAIL): r3 probe -- `c //= b` (b may be 0: ZeroDivisionError) -- now REFUSED (PYCSL-R447-AUGASSIGN-DIVISION); was an ill-formed `c := !c div b`.
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(a: int, b: int) -> int:
    c = a
    c //= b
    return c
