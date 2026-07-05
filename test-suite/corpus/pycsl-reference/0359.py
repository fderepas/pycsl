"""Test 0359 — ZeroDivisionError baseline (no annotation).

Today's PyCSL proves this with the existing `requires y <> 0` VC
emitted by `pycsl_div`. The test exists so we can spot regressions
on the baseline when `no_exception` changes the surrounding code.
"""
_ = 0  # anchor
#@ requires n != 0
#@ ensures \result == 256 // n
#@ assigns \nothing
def divide_256(n: int) -> int:
    return 256 // n


if __name__ == "__main__":
    assert divide_256(4) == 64
