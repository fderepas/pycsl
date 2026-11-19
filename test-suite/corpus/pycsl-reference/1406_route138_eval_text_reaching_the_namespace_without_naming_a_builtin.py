r"""Test 1406 — ROUTE #138: the #136 eval-token rule fires only when the constant text names one of the eight `_nb_ns_builtins`. `eval("f.__globals__.__setitem__(chr(78), 5)")`-style text names none of them; measured with `eval("f.__globals__.__setitem__(\x27N\x27, 5)")`, which PROVED `f() == 3` while CPython returns 5. A constant eval text carrying a call, an attribute or a subscript is now refused wherever it stands.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


eval("f.__globals__.__setitem__('N', 5)")