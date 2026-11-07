r"""Test 2700 — route #259 (expected FAIL): `2 ** n` with `n < 0` is a FLOAT in Python
(`2 ** -1 == 0.5`), but `**` lowered to the int-valued `val function py_pow`, so the
integrality test `x % 1 == 0` PROVED `\result == True` at b35d9c5e. CPython: f(-1) is False.
Now `py_pow` owes `y >= 0` at every program call; a negative exponent cannot discharge it.
"""
# pycsl-expected: FAIL


#@ requires n < 0
#@ ensures \result == True
#@ assigns \nothing
def f(n: int) -> bool:
    x = 2 ** n
    return x % 1 == 0


if __name__ == "__main__":
    assert f(-1) is False
