r"""Test 2706 — route #259 (expected FAIL): `pow(2, exp=n)` — the generic call arm DROPS
keywords, giving `pow_1 2`, an int with no exponent left to guard. CPython: f(-1) is False
(`0.5 % 1`). Now a keyword `pow` call owes an undischargeable obligation (fail closed).
"""
# pycsl-expected: FAIL


#@ requires n < 0
#@ ensures \result == True
#@ assigns \nothing
def f(n: int) -> bool:
    x = pow(2, exp=n)
    return x % 1 == 0


if __name__ == "__main__":
    assert f(-1) is False
