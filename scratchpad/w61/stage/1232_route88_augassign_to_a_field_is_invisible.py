"""Test 1232 — ROUTE #88: an `AugAssign` to a field is invisible to every capture path.

Neither `Module5_IREmitter._collect_class_fields` nor
`construction_synth._collect_init_construction` looks at `ast.AugAssign`, so `self.n += 5` left
the field at the literal `0` its first store gave it. Measured before the repair: this claim
PROVED, CPython returns 5.

An augmented store is never reducible to a single record literal, so the field's value at
construction time is genuinely UNKNOWN and the repair marks it `(any int)` — the same
conclusion route #83 reached for a conditional store, and the same fallback route #79 uses.
**PREFER A FAITHFUL CAPTURE WHEREVER THE INFORMATION EXISTS AND FALL BACK TO UNCONSTRAINED ONLY
WHERE IT GENUINELY DOES NOT**: 1229 and 1231 are the faithful half of this route, this file and
1233 are the honest unconstrained half. The TRUE claim `\result == 5` is REFUSED here too, and
that is recorded rather than hidden — constant-folding an augmented store is a general
evaluator, not a capture rule.

This file is `pycsl-expected: FAIL`.
"""
# pycsl-expected: FAIL


class C:
    n: int

    #@ assigns self.n
    def __init__(self) -> None:
        self.n = 0
        self.n += 5


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.n
