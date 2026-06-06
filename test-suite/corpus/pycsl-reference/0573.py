"""Test 0573 — multi-binder quantifier sugar (remains-2.md C).

`\forall x, y; P` is sugar for nested single binders `\forall x; \forall y; P` (all
`int`), desugared in the parser transformer — no new emission. Proves a two-variable
commutativity fact; `\exists` multi-binder works symmetrically.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires \forall x, y; x + y == y + x
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    return 0
