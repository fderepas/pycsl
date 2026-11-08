r"""Test 1402 — ROUTE #137: #118's namespace-dict rule enumerates the DICT spellings (`globals()[k]`, `vars()[k]`, `<mod>.__dict__[k]`), and a module def's `__globals__` IS that same dict under a name the rule never listed: `f.__globals__["N"] = 5` PROVED `f() == 3` while CPython returns 5. A SUBSCRIPT store at module or class-body scope is now keyed on the PATH being written — the receiver must be a name this file can describe — exactly like the attribute sink.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
N = 3


#@ ensures \result == N
#@ assigns \nothing
def f() -> int:
    return N


f.__globals__["N"] = 5
