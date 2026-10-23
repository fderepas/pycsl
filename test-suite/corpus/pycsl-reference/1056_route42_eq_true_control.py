"""Test 1056 — ROUTE #42 CONTROL: `<int> == True` is CORRECT and must keep proving.

TRUE OF THE PROGRAM: Python's `1 == True` is True, so `f()` returns 7.

This is the control that localizes route #42 to `is`. `==` is VALUE equality and the
bool-as-int convention models it faithfully — `True == 1` is Python's own answer. The
route-#42 fix must NOT touch this shape, and this driver is what says so: if a later
change starts refusing or erasing `== True`, this test goes red rather than silently
losing the idiom `#@ ensures \\result == True` depends on.
"""
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = 1
    if x == True:
        return 7
    return 0
