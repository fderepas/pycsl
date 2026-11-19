r"""Test 7544 -- route #476 (expected FAIL): n2_module_call_frontier -- driver probe: the frontier is a module-level call of `f` (no main guard), `g` rebound after it; CPython ZeroDivisionError. Already REFUSED at 8aaa864ca by the import-time-call rule; now REFUSED by route #476 first (PYCSL-R476-REBOUND-AFTER-FRONTIER), which judges the binding live at the frontier whatever spells it.
"""
# pycsl-expected: FAIL
def g(x: int) -> int:
    return 1 // (x - x)


#@ no_exception \all
def f(n: int) -> int:
    return g(n)


try:
    print(f(1))
except Exception as e:
    print("VIOLATION", type(e).__name__, e)


def g(x: int) -> int:
    return x
