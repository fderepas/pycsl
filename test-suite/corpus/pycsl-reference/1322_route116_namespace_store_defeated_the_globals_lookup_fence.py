r"""Test 1322 — ROUTE #116 second-order carrier (and #118's root): a genuine globals-lookup helper
`_N` over `_g = globals()` passed batch-2's fence, but a module-level SUBSCRIPT store
`_g["inc"] = dec` changed what `_N("inc")` returns, and `(inc 3)` still PROVED
`\result == 4` (CPython 2). A store through the module namespace is now refused with
route #118's rebinding refusal.
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


_g = globals()


def _N(name):
    return _g[name]


_g["inc"] = dec


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return _N("inc")(3)
