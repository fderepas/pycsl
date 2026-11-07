r"""Test 2396 — route #249 (expected PASS): CONTROL: builtin `str` parameters keep Why3 `=`: `requires x == y` PROVES `ensures y == x`.
"""
# pycsl-expected: PASS
#@ requires x == y
#@ ensures y == x
#@ assigns \nothing
def f(x: str, y: str) -> int:
    return 0


if __name__ == "__main__":
    assert ("ab" == "ab") and ("ab" == "ab")
