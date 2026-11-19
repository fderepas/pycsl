"""Test 1028 — ROUTE #37 negative witness: the `else:` block of a `try` was
DROPPED when it jumps out.

FALSE OF THE PROGRAM: no exception is raised, so Python runs the `else` clause
and returns 2.

At the parent commit c4233fed this proved `\result == 1`, and the emitted body
contained no trace of `return 2` at all. `_handle_try_stmt` appends the lowered
`else` to the try body ONLY when `"raise" not in <lowered else>` — and a `return`
lowers to `raise (Return ...)`, so an else block that RETURNS is dropped in
silence.

THE RATCHET WAS GREEN THE WHOLE TIME, which is the part worth keeping.
`bin/check-dropped-mutation.py` classifies exactly this shape as TRYFINAL and its
ratchet stands at 10: the drop was COUNTED. Counting a drop is not the same as
establishing that it is safe — route #21 proved that for the `finally` half and
refused it; the `else` half was left counted and unrefused on the same evidence.
An `else:` that CANNOT jump out is still modelled — see 1029.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    try:
        x = 1
    except ValueError:
        return 3
    else:
        return 2
    return 1
