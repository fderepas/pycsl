r"""Test 2348 — route #247 (expected FAIL): PEP 484's numeric tower admits an `int` for a `float`
parameter, but the declared `float` decided `isinstance(x, int)` FALSE (`(2 = 0)`); `\result == 0`
PROVED at afe28c69. CPython `f(1)` = 1.
"""
# pycsl-expected: FAIL


#@ ensures \result == 0
#@ assigns \nothing
def f(x: float) -> int:
    if isinstance(x, int):
        return 1
    return 0


if __name__ == "__main__":
    assert f(1) == 1
