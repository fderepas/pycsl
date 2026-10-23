r"""Test 1367 — ROUTE #132: `N = 3` then `N += 2`; the constant folder counts only top-level single-name `Assign`/`AnnAssign`, folded `N` to 3 and PROVED `f() == 3` while CPython returns 5 (the same premise was also used in a `requires`).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
N = 3
N += 2


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
