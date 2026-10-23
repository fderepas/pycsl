r"""Test 1369 — ROUTE #132 (alias arm): the str dict `OP` is folded to its literal; `d = OP; d["a"] = "c"` inside `f` mutates the same object through an alias (lowered as a no-op on an opaque int), so `OP.get("a", "")` PROVED `== "b"` while CPython returns "c". Every reference to a folded mutable literal must now be a read.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
OP = {"a": "b"}


#@ ensures \result == "b"
#@ assigns \nothing
def f() -> str:
    d = OP
    d["a"] = "c"
    return OP.get("a", "")
