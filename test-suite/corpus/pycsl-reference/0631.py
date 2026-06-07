"""Test 0631 — negative: `\in_globals` of an undeclared name is WITHHELD (07-1839 P2 anti-unsoundness).

The world is open (import/exec inject names), so `\in_globals` is three-valued and true-only: an
undeclared name resolves to UNKNOWN (an uninterpreted bool), never decided-true. Asserting
`\in_globals(nonexistent_name)` therefore cannot be proven — PyCSL refuses to over-claim membership.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare


#@ ensures \in_globals(nonexistent_name)
#@ assigns \nothing
def f() -> int:
    return 0
