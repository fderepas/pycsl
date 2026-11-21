"""Test 1228 — ROUTE #88: a scalar field's **LAST** store in `__init__` loses to its **FIRST**.

`Module5_IREmitter._collect_class_fields` guarded every store with `target.attr not in
field_names_seen`, so the FIRST store to a field decided its `field_defaults` entry and every
later store was skipped outright. The emitted WhyML for this class was literally
`let c = { n = 1 } in c.n`. Measured before the repair: this claim PROVED, CPython returns 2,
and the TRUE twin (1229) was REFUSED.

**HOW IT WAS FOUND.** Generator 1 from gen #10's handoff, applied to the `__init__`
field-capture family that had already yielded routes #79, #82, #83, #85 and #87: *which single
operation did every one of those controls actually run?* Every one of them ran a constructor
that writes each field EXACTLY ONCE. The second store is a different operation and nobody had
run it. First probe batch of gen #11, four files, one hit.

**THE SHARPEST PART IS THAT THE RULE WAS ALREADY WRITTEN DOWN.** Route #79's comment in
`module5/construction_synth.py` states it verbatim — *"THE UNIT IS THE FIELD'S LAST TOP-LEVEL
STORE, NOT THE STORE. A field written twice must be judged by the write that decides its
value"* — and `_last79` implements it correctly for the UNKNOWN-MARKING decision only. The two
VALUE-supplying paths never got the same treatment. **A RULE STATED IN A COMMENT IS NOT A RULE
THE OTHER FUNCTIONS OBEY.**

This file is `pycsl-expected: FAIL`.
"""
# pycsl-expected: FAIL


class C:
    n: int

    #@ assigns self.n
    def __init__(self) -> None:
        self.n = 1
        self.n = 2


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.n
