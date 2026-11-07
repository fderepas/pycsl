r"""Test 4604 -- gen #37 route #340 (expected FAIL): `x += 1` after `def g(y=x)`: PROVED `\result == x + 1` (CPython: the old `x`). REFUSED now (PYCSL-SEM-DEF-TIME-EVALUATION, route #340).
"""
# pycsl-expected: FAIL
#@ ensures \result == x + 1
def f(x: int) -> int:
    def g(y: int = x) -> int:
        return y
    x += 1
    return g()

if __name__ == "__main__":
    assert f(1) == 2
