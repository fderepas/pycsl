"""Test 1062 — ROUTE #44 control: `x = None; x is None` is TRUE and must keep proving.

TRUE OF THE PROGRAM: Python returns 7.

The half of route #44 that must NOT become undecidable. The fix makes the READ of a
`None`-bound local the opaque `pycsl_none`, and the `is None` fall-through compares
against that SAME constant — so the test is `pycsl_none = pycsl_none`, which is exactly
Python's answer. A fix that made the value opaque without making the comparison use the
same constant would have turned this into a completeness regression, which is why this
driver exists rather than being assumed.
"""
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = None
    if x is None:
        return 7
    return 0
