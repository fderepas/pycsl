r"""Test 2213 — route #239 (expected PASS): CONTROL for 2207. Two reads of ONE erased binding
agree (`!x` twice after one `x := (any int)`), so `\result == 1` PROVES; CPython `f()` = 1.
"""
# pycsl-expected: PASS


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    x = (1, 2)
    a = x
    b = x
    if a == b:
        return 1
    return 0
