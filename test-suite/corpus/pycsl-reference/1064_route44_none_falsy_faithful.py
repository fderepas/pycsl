"""Test 1064 — ROUTE #44 control: `bool(None)` is False, and that stays DECIDED.

TRUE OF THE PROGRAM: `if None:` is not taken, so Python returns 0.

Route #44 records a `None`-bound local in the SAME dict routes #25/#26/#27/#41 use to
REFUSE a local's truthiness — and that would have been wrong here. A generator or a
non-empty tuple is always truthy while the model reads `0`, so refusing is right for
them; `None` is FALSY and the literal `0` is the model's correct answer. So the record
carries the `#empty` suffix that keeps `_to_bool` out of it, and only the VALUE is
opaque. Without this driver the distinction is invisible: the opaque value alone would
turn this into `pycsl_none <> 0`, undecidable, and a true contract would stop proving.
"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = None
    if x:
        return 7
    return 0
