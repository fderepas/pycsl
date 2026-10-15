r"""Test 2249 — route #240 (expected FAIL): a subject DECLARED `bool` decided `isinstance(b,
bool)` TRUE, but the model admits an INT actual for a `bool` parameter (both lower to `int`):
`f`'s `ensures \result == 1` PROVED at 1e4b380e and `m`'s call `f(5)` inherited it, while
CPython `f(5)` = 0 (`m()` = 0). A bool test on any int-modelled subject is now undecided; `f`'s
postcondition is unproved.
"""
# pycsl-expected: FAIL


#@ ensures \result == 1
#@ assigns \nothing
def f(b: bool) -> int:
    if isinstance(b, bool):
        return 1
    return 0


#@ ensures \result == 1
#@ assigns \nothing
def m() -> int:
    return f(5)
