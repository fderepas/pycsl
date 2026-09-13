# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL
"""1288 — (#49) ROUTE #101 EXPLOIT ARM: a SINGLE-INDEX `#@ assigns seq[idx]` on a bodyless
`val` emitted NO `writes` CLAUSE AT ALL, and a `val` with no `writes` is the STRONGEST
possible claim — Why3 is told the stub is PURE.

MECHANISM, read off the emitted WhyML rather than inferred. `_emit_frame_condition` built a
bodyless val's frame from exactly TWO collector loops, one keyed on `Attribute`/`FieldGet`
and one on `AssignsRegion`. `Module2_Parser._parse_assigns_region` does `expect_op("..")`,
so a LONE index fails that `_try` and falls through to the generic expression parse, landing
in the IR as `{"type": "Subscript"}` — which matched NEITHER loop, and, the crux, never
reached `_unframed_regions` either, so ROUTE #98'S OWN REFUSAL — installed precisely to stop
a bodyless val silently losing its frame — COULD NOT FIRE.

MEASURED AT 1bf3c768, same stub / same body / same `requires`, only the spelling differing:

    #@ assigns seq[idx]    ->  no `writes`        ->  `ensures \\result == 7` PROVES
    #@ assigns seq[0..1]   ->  `writes { seq }`   ->  the same `ensures` FAILS

and CPython returns 5. IT SHIPPED: `src/pycsl_lib/oper/__init__.py:175` carries
`#@ assigns seq[idx]`, and `frontend/ir_resolve.py:201` stamps every imported function
`trusted = True`, so an ordinary program with NO `\\trusted` marker of its own exploited it.

>>> A REFUSAL INSTALLED TO OBSERVE A RESIDUE IS KEYED ON THE SPELLING ITS AUTHOR WAS LOOKING
>>> AT. THE OBLIGATION IS ABOUT THE *PATH BEING WRITTEN*; THE GUARD WAS WRITTEN ABOUT THE
>>> *NODE TYPE THAT HAPPENED TO CARRY IT*.

Must FAIL: the frame is now built from the RESOLVED write path, so `writes { seq }` is
emitted and the caller can no longer prove the array unchanged.
"""


#@ \trusted reviewer: route101
#@ requires \length(seq) > 0
#@ requires idx >= 0
#@ requires idx < \length(seq)
#@ assigns seq[idx]
def setcell(seq: list, idx: int, v: int) -> None:
    seq[idx] = v


#@ requires \length(a) > 0
#@ requires a[0] == 7
#@ ensures \result == 7
def driver(a: list) -> int:
    setcell(a, 0, 5)
    return a[0]
