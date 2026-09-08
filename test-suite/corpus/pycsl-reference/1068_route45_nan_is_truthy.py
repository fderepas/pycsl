"""Test 1068 — ROUTE #45 control: `bool(nan)` is TRUE, the opposite of `bool(None)`.

TRUE OF THE PROGRAM: NaN is not zero, so `if x:` is taken and Python returns 7.

Route #45 records a NaN-bound local in the SAME dict routes #25/#26/#27, #41 and #44 use,
and the truthiness answer differs for every one of them: refused for a generator or a
non-empty tuple (always truthy, model reads 0), `false` for `None` (falsy), `true` here.
That is why route #45's record carries no `#empty` suffix and gets its own `_to_bool` arm —
and why this driver exists rather than the distinction being assumed. At the parent commit
3bbfb59f this FAILED.
"""
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = float("nan")
    if x:
        return 7
    return 0
