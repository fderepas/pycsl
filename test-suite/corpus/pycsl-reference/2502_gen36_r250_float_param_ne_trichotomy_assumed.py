r"""Test 2502 — route #250 (expected PASS UNDER THE DECLARED MODEL ASSUMPTION FLOAT-FINITE).

A `float` parameter with `requires x != y` / `ensures x < y or y < x`. The default model is Why3 `real`, which has no NaN, so the claim
PROVES; CPython REFUTES it for `x = float("nan")` (see `__main__`). This is NOT a soundness bug of
the default mode: it is the counterexample of the declared assumption FLOAT-FINITE ("every float
value is finite and non-NaN"), which `pycsl --soundness-report` lists for this file and the
reference docs state. Twin 2505 runs the same file under `--strict-float-finite`, where the
assumption is dropped and the claim FAILS.
"""
# pycsl-model-assumption: FLOAT-FINITE
# pycsl-expected: PASS


#@ requires x != y
#@ ensures x < y or y < x
#@ assigns \nothing
def f(x: float, y: float) -> int:
    return 0


if __name__ == "__main__":
    x, y = float("nan"), 1.0
    print(f(x, y), x != y, x < y or y < x)  # 0 True False: FALSE for NaN
