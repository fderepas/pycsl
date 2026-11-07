r"""Test 4605 -- gen #37 route #340 (expected FAIL): `i = 0; def g(y=i)` (`1 // y`), `i = 5; g()` under `no_exception \all`: PROVED (CPython ZeroDivisionError). REFUSED now (PYCSL-SEM-DEF-TIME-EVALUATION, route #340).
"""
# pycsl-expected: FAIL
#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    i = 0
    #@ requires y > 0
    #@ no_exception \all
    def g(y: int = i) -> int:
        return 1 // y - 1 // y
    i = 5
    return g()

if __name__ == "__main__":
    assert f() == 0
