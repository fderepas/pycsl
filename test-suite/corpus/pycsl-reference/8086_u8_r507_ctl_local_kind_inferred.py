r"""Test 8086 -- routes #507 / #508 / #509 (control, expected PASS): an unannotated local `k = n; k += 3` is read as an int and `"ab" * k` is a plain statement discharged by the requires; CPython f(5, 0.5) returns 1
"""
# pycsl-expected: PASS
#@ requires 0 <= n and n <= 1000
#@ no_exception \all
#@ ensures \result == 1
def f(n: int, x: float) -> int:
    k = n
    k += 3
    t = "ab" * k
    v = {t}
    return 1
