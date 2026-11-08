r"""Test 2708 — route #259 CONTROL (expected PASS): `x ** n` under `requires n >= 0` is an
int in Python; the new `py_pow` obligation `n >= 0` is discharged from the precondition,
so the TRUE integrality claim still proves (and `x ** 2` discharges it from the literal).
"""


#@ requires n >= 0
#@ ensures \result == True
#@ assigns \nothing
def f(x: int, n: int) -> bool:
    y = x ** n
    z = x ** 2
    return y % 1 == 0 and z % 1 == 0


if __name__ == "__main__":
    assert f(3, 2) is True and f(-5, 0) is True
