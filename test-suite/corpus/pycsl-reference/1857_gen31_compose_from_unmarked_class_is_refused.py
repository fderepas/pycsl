r"""Test 1857 — gen #31 WITNESS: `#@ compose_from` naming a class that is not `#@ mixin`.

annotations.md §2.7 row 1: "Mixin — `#@ mixin` — `class` — Marks the class as a composable
mixin (not instantiated directly)." Both halves of that sentence were measured ABSENT:

  * the flagship driver 0549 with `#@ mixin` DELETED from `CoreEmit` — still named in
    `#@ compose_from CoreEmit, MapOps` — composed and VERIFIED exactly as before;
  * a `#@ mixin` class instantiated directly verified too, and so did the same file with
    the marker removed, so the two halves were indistinguishable.

`ir_resolve.apply_composition` reads the names off the `#@ compose_from` line and never
consulted the marker. Found by `bin/check-directive-enforcement.py` while trying to write
the directive's enforcement pair: there was no violating program to write, which is that
plane's third kind of answer.

NOT A SOUNDNESS HOLE — the flatten-and-re-verify compensation (S2b, finding w66) does not
depend on the marker, so deleting it removed a LABEL and not a check. What was at risk is
the READING: "this class is a mixin, so it is never instantiated, so I need not reason
about its `__init__` or its class invariant standing alone."

REFUSED AT `_run_pipeline` RATHER THAN IN `apply_composition`, and that is a measurement
rather than a preference. The natural home reads `is_mixin` off the class's `type_decl`,
and **`type_decls` is EMPTY for exactly the classes that are mixins**: a class with no
fields and no `__init__` produces no record decl, and the flagship mixin shape has neither.
Instrumented, `apply_composition` printed `DBG decls: [] mixins: ['CoreEmit', 'MapOps']` —
the pass cannot see the marker it would need.

This file is 0549's shape with `#@ mixin` removed from `CoreEmit`. Control: 1858, the same
file with the marker restored, which verifies.

STILL OPEN: the other half of the sentence — a `#@ mixin` class must not be INSTANTIATED
directly — is not yet enforced. See `finding-mixin-marker-has-no-teeth.md`.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


class CoreEmit:
    #@ shared_state program_ir: int
    #@ provides emit
    #@ ensures \result >= 0
    #@ assigns \nothing
    def emit(self, x: int) -> int:
        return x if x >= 0 else 0


#@ mixin
class MapOps:
    #@ depends_method emit: (self, x: int) -> int
    #@   ensures \result >= 0
    #@ provides handle_get
    #@ ensures \result >= 0
    #@ assigns \nothing
    def handle_get(self, k: int) -> int:
        return self.emit(k)


#@ compose_from CoreEmit, MapOps
class Facade:
    #@ ensures \result >= 0
    #@ assigns \nothing
    def run(self, k: int) -> int:
        return self.handle_get(k)
