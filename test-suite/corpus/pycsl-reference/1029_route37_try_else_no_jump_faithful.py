"""Test 1029 — ROUTE #37 POSITIVE witness: an `else:` that cannot jump out is
still modelled, and faithfully.

No exception is raised, so Python runs the `else` and returns 2. The refusal
added for 1028 is scoped to an else block containing a `return`/`raise`/`break`/
`continue` — the shapes whose lowering carries a `raise` and therefore get
dropped — so the capability #33 added survives it.
"""
_ = 0  # anchor
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    y = 0
    try:
        x = 1
    except ValueError:
        y = 3
    else:
        y = 2
    return y
