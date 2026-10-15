r"""Test 2250 — route #240 (expected PASS): CONTROL. `isinstance(<bool>, int)` stays DECIDED TRUE
(bool is a subclass of int, and an int actual is an int too), so `\result >= 1` PROVES — CPython
`f(True)` = 2 and `f(5)` = 1. Only the converse direction, the `bool` test, became undecided.
"""
# pycsl-expected: PASS


#@ ensures \result >= 1
#@ assigns \nothing
def f(b: bool) -> int:
    r = 0
    if isinstance(b, int):
        r = r + 1
    if isinstance(b, bool):
        r = r + 1
    return r
