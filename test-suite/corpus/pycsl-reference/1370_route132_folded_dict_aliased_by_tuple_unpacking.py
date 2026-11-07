r"""Test 1370 — ROUTE #132 (alias arm, order 2): `d, e = OP, 1; d["a"] = "c"` at module scope escaped the first repair draft, which enumerated the alias SPELLING `d = OP`; `OP.get("a", "")` PROVED `== "b"` while CPython returns "c".
"""
# pycsl-expected: FAIL
_ = 0  # anchor
OP = {"a": "b"}
d, e = OP, 1
d["a"] = "c"


#@ ensures \result == "b"
#@ assigns \nothing
def f() -> str:
    return OP.get("a", "")
