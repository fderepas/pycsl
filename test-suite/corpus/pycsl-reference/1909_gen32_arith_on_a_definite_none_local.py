r"""Test 1909 — gen #32 (expected FAIL): ROUTE #227, the headline witness.

FALSE OF THE PROGRAM: `None - None` raises `TypeError` in Python, so this function has no
value at all — and at the parent commit `c85bdb05` it PROVED `\result == 3` **and**
`#@ no_exception \all`.

THE RESIDUE OF A REPAIR, NOT AN OVERSIGHT. Routes #44/#184/#191 replaced the definite
integer `0` that a `None` read used to lower to with the opaque `val function pycsl_none :
int` "with NO defining axiom". That genuinely closed `v == 0`. But the opaque still inhabits
`int`, so every law of integer arithmetic still applies to it, and the falsehood moved from
the VALUE to the TYPE: `pycsl_none - pycsl_none` is `0` by a theorem about `int`, no matter
what the opaque denotes.

Route #44's own negative witness `1060_route44_none_arith.py` is this shape with `x + 5` —
value-DEPENDENT, so the opaque closed it — and its docstring says "an equality-only fix
would have been the same mistake one operator later". It was arithmetic-aware and still
stopped one ALGEBRAIC IDENTITY short. `v == 0` is the probe the repair was built to defeat;
`v - v` is the one nobody wrote.

1060 now fails by this same REFUSAL rather than by an undecided postcondition.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 3
#@ no_exception \all
#@ assigns \nothing
def f() -> int:
    v = None
    return v - v + 3
