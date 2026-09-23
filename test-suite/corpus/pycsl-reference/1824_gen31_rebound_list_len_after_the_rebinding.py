r"""Test 1824 — gen #31: `len()` of a literal-rebound list local, AFTER the rebinding.

With `n > 0` the rebinding runs and `a` is `[1, 2]`, so CPython answers 2 — while the
backing Why3 array still has length 3. Before gen #31 `len` lowered to `Array.length a` and
would have answered 3; it now reads the counter the rebinding maintains.

Pairs with 1823 (the same function, the other path).
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ requires n > 0
#@ ensures \result == 2
def f(n: int) -> int:
    a: list = [7, 8, 9]
    if n > 0:
        a = [1, 2]
    return len(a)
