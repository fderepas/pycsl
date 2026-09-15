r"""Test 1324 — ROUTE #118 walrus carrier: `if (inc := dec): pass` at module level rebinds
`inc`, and `inc(3)` was modelled against `def inc` (`\result == 4` PROVED, CPython 2). The
first draft of the rebinding refusal enumerated statement KINDS and missed it; the refusal is
keyed on every NAME binding in the scope.
"""
# pycsl-expected: FAIL
#@ ensures \result == y + 1
#@ assigns \nothing
def inc(y: int) -> int:
    return y + 1


#@ ensures \result == y - 1
#@ assigns \nothing
def dec(y: int) -> int:
    return y - 1


if (inc := dec):
    pass


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return inc(3)
