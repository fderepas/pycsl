"""Test 0635 — \in_scope decides TRUE for definitely-assigned names (07-1839 P3).

Definite-assignment: a name bound on ALL paths to a point is in scope. A formal parameter (`x`)
and a top-level local assigned before any branching (`y = 5`) are both definitely assigned, so
`\in_scope(x)` and `\in_scope(y)` lower to `true` and prove.
"""
# pycsl-flags: --memory-model hoare


#@ ensures \in_scope(x)
#@ ensures \in_scope(y)
#@ assigns \nothing
def f(x: int) -> int:
    y = 5
    return x + y
