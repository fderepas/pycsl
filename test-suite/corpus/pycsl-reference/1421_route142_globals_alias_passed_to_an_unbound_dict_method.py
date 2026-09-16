r"""Test 1421 — ROUTE #142: the namespace-escape rules permit binding the mapping to a plain NAME (route #116`s `_g = globals()` idiom). That name was then an unguarded handle: `_g = globals(); dict.update(_g, N=5)` PROVED `f() == 3` while CPython returns 5. A name bound to a namespace mapping is now itself a namespace mapping, and may only be read through a subscript.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
N = 3
_g = globals()
dict.update(_g, N=5)


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N