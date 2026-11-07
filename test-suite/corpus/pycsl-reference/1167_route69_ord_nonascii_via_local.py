"""1167 — ROUTE #69 NEGATIVE: the same, one binding away.

The first version of the repair refused only `ord(<non-ASCII literal>)` and this spelling
walked straight past it — the fifth time in one generation that a guard keyed on a syntactic
LOCATION was defeated by moving the hazard one step. The guard is now keyed on the BINDING.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result < 256
#@ assigns \nothing
def f() -> int:
    s = "€"
    return ord(s[0])
