r"""Test 1823 — gen #31: `len()` of a literal-rebound list local, BEFORE the rebinding.

With `n == 0` the rebinding does not run and `a` is still `[7, 8, 9]`, so CPython answers 3.
The counter is initialised to the FIRST literal's length precisely so this path is right;
initialising it to 0 like an append target would have made this file fail.

Its false twin is 1825 (`== 2` on the same path). 1824 is the other direction.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ requires n == 0
#@ ensures \result == 3
def f(n: int) -> int:
    a: list = [7, 8, 9]
    if n > 0:
        a = [1, 2]
    return len(a)
