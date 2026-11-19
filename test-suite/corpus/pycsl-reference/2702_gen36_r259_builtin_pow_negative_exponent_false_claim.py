r"""Test 2702 — route #259 (expected FAIL): builtin `pow(2, n)` is `2 ** n` — a float for
`n < 0` — but lowered to the opaque INT `val pow_2`, so `x % 1 == 0` PROVED at b35d9c5e.
CPython: f(-1) is False. Now `pow_2` owes `x1 >= 0` like `py_pow`.
"""
# pycsl-expected: FAIL


#@ requires n < 0
#@ ensures \result == True
#@ assigns \nothing
def f(n: int) -> bool:
    x = pow(2, n)
    return x % 1 == 0


if __name__ == "__main__":
    assert f(-1) is False
