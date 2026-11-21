r"""Test 2462 — route #251 (expected PASS): CONTROL: `float` parameters keep the ordering of the `real` model: `requires x
< y` still PROVES `ensures not (y < x)` (true in CPython, NaN included: `x < y` True rules NaN out).
"""
# pycsl-expected: PASS
#@ requires x < y
#@ ensures not (y < x)
#@ assigns \nothing
def f(x: float, y: float) -> int:
    return 0


if __name__ == "__main__":
    for x, y in ((0.5, 1.5), (-2.0, 3.25), (1.0, float("inf"))):
        assert x < y and not (y < x)
