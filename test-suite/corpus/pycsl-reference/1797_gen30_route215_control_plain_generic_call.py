r"""Test 1797 — CONTROL for route #215: the PLAIN call of a generic function is untouched.

`ident(1)` (no subscript) IS valid Python and IS lowered faithfully — the emission is
`a := (ident 1)`, not an erased constant — so this file compiles and its TRUE contract
verifies. The route's refusal must not touch it.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ requires n >= 0
#@ ensures \result == n
def ident[T](n: int) -> int:
    return n


#@ ensures \result >= 0
def probe() -> int:
    a = ident(1)
    return a
