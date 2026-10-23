r"""Test 1756 — WITNESS: a constant `exec(...)` containing control flow.

The exec splice inlines a CONSTANT exec's body as straight-line code, which is
verification-equivalent to writing it inline. A whitelist bars control flow, because
splicing an `if` would change what the surrounding contract means. Sibling: 1757 (an exec
whose literal does not parse at all).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 1
def f() -> int:
    exec("if True:\n    x = 1\n")
    return 1
