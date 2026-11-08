"""Test 1053 — ROUTE #42 negative witness (a): `<int> is True` was DECIDABLY TRUE.

FALSE OF THE PROGRAM: Python's `1 is True` is False, so `f()` returns 0.

`is` is object identity against the `True` SINGLETON, and a genuine `int` is never
that singleton. At the parent commit 0f3906bd this PROVED `\\result == 7`, because
Module 5 mapped `ast.Is` onto `"=="` (`_PY_OP_MAP`) and Module 6's bool-as-int
convention rewrote the `True` literal operand of `==` to `1` — two defensible
conventions that together made `is` and `==` THE SAME OPERATOR on a bool literal.

The fix gives the IR a DISTINCT `is` operator and whitelists the bool-singleton
test: admitted only when the emitter can SHOW the other operand is a Python `bool`
(1057 is that control). Here `x` is an int-valued local, so it fails closed.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = 1
    if x is True:
        return 7
    return 0
