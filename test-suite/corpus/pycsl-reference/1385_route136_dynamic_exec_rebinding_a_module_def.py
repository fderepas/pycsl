r"""Test 1385 — ROUTE #136: a dynamic `exec` rebinding a module-level `def`. The CONSTANT twin is refused by #118 ("a constant `exec` naming a function or class"); the dynamic one PROVED `inc(3) == 4` while CPython returns 2.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == y + 1
#@ assigns \nothing
def inc(y: int) -> int:
    return y + 1


exec("in" + "c = lambda y: y - 1")


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return inc(3)
