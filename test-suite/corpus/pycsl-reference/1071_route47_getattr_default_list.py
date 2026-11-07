"""Test 1071 — ROUTE #47 negative witness (b): a LIST default was the integer 0 too.

FALSE OF THE PROGRAM: `[] == 0` is False in Python, so `f()` returns 0.

The list half of 1070. Both halves matter for the same reason witness 1054 matters to route
#42 and 1044 to route #41: a fix keyed on one literal kind would have been the same mistake
one kind later. At the parent commit d7ce974c `\\result == 7` PROVED.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    #@ requires True
    #@ ensures True
    def __init__(self) -> None:
        self.x = 1


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    c = C()
    d = getattr(c, "missing", [])
    if d == 0:
        return 7
    return 0
