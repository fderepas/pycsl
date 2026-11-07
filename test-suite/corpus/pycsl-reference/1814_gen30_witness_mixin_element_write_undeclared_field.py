r"""Test 1814 — WITNESS: a mixin method writing an UNDECLARED self field BY ELEMENT.

Corpus 0551 is the same program with `self.cache = x`, and it is refused with

    Mixin 'CoreEmit' (composed into 'Facade'): a method writes `self.cache`, a field
    declared neither `#@ shared_state` nor `#@ touches_field` nor initialised in __init__.

This file writes `self.cache[0] = x` — ONE CHARACTER APART — and it was ACCEPTED, and the
emitted module type-checked. The guard's population was `self_field_writes(body)`, which
matched `FieldAssign` / `FieldAugAssign` on `self`; an element write is emitted as
`{"stmt": "ArraySet", "array": {"type": "FieldGet", "object": "self", ...}}` and was
invisible to it. Lesson (t3): ask what never ENTERS the collection the guard iterates.

IT IS A DIAGNOSTIC GAP, NOT A SOUNDNESS ONE, and that was checked rather than assumed. With
the field made real in the facade, a `#@ assigns \nothing` mixin method writing
`self.cache[0]` and a facade reading the element either side of the call gives CPython -7
and PyCSL `[-] Verification FAILED`: the CLONE carries `ensures { self.cache = old
self.cache }` and the element write makes it unprovable. **The frame check catches what
this guard missed** — what was lost is the SENTENCE that tells the user which field to
declare, which is the only thing this guard exists to produce.

THE CONTROL IS THE GUARD'S SILENCE, not another PASS: a mixin whose element write is on a
DECLARED field is not refused by this check — the program still fails, with a TYPE error
from a separate, pre-existing gap (a list field in a mixin is not modelled), and the
message says which. 0554, 0549, 0553, 0968 and the two route-#95 controls all still PASS
unchanged.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ mixin
class CoreEmit:
    #@ shared_state program_ir: int
    #@ provides emit
    #@ ensures \result >= 0
    #@ assigns \nothing
    def emit(self, x: int) -> int:
        self.cache[0] = x
        return x if x >= 0 else 0


#@ compose_from CoreEmit
class Facade:
    #@ ensures \result >= 0
    #@ assigns \nothing
    def run(self, k: int) -> int:
        return self.emit(k)
