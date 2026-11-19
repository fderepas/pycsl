r"""Test 2505 — route #250 (expected FAIL): `--strict-float-finite` drops FLOAT-FINITE.

Same program as 2502: a `float` parameter with `requires x != y` / `ensures x < y or y < x`. Under the flag every float comparison
and `==` also requires its operands to differ from the NaN sentinel (the non-dyadic real `1/3`, a
definition — no axiom), so the claim, FALSE in CPython for `x = float("nan")`, no longer proves.
"""
# pycsl-flags: --strict-float-finite
# pycsl-expected: FAIL


#@ requires x != y
#@ ensures x < y or y < x
#@ assigns \nothing
def f(x: float, y: float) -> int:
    return 0


if __name__ == "__main__":
    x, y = float("nan"), 1.0
    print(f(x, y), x != y, x < y or y < x)  # 0 True False: FALSE for NaN
