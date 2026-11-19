r"""Test 4602 -- gen #37 route #340 (expected FAIL): `x = 1; def g(y=x); x = 2; return g()` PROVED `\result == 2` (CPython 1: the default is bound at def time). REFUSED now (PYCSL-SEM-DEF-TIME-EVALUATION, route #340).
"""
# pycsl-expected: FAIL
#@ ensures \result == 2
def f() -> int:
    x = 1
    def g(y: int = x) -> int:
        return y
    x = 2
    return g()

if __name__ == "__main__":
    assert f() == 2
