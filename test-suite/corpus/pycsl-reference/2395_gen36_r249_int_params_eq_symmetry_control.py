r"""Test 2395 — route #249 (expected PASS): CONTROL: builtin `int` parameters keep Why3 `=`: `requires x == y` PROVES `ensures y == x` (true in
CPython for every pair of ints).
"""
# pycsl-expected: PASS
#@ requires x == y
#@ ensures y == x
#@ assigns \nothing
def f(x: int, y: int) -> int:
    return 0


if __name__ == "__main__":
    for x, y in ((1, 1), (2, 2), (-3, -3)):
        assert (x == y) and (y == x)
