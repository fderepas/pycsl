r"""Test 2504 — route #250 (expected FAIL): `--strict-float-finite` drops FLOAT-FINITE.

Same program as 2501: a `float` parameter with `ensures x <= x`. Under the flag every float comparison
and `==` also requires its operands to differ from the NaN sentinel (the non-dyadic real `1/3`, a
definition — no axiom), so the claim, FALSE in CPython for `x = float("nan")`, no longer proves.
"""
# pycsl-flags: --strict-float-finite
# pycsl-expected: FAIL


#@ ensures x <= x
#@ assigns \nothing
def f(x: float) -> int:
    return 0


if __name__ == "__main__":
    x = float("nan")
    print(f(x), x <= x)  # 0 False: the claim is FALSE for NaN
