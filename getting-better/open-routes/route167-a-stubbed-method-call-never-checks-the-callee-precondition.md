# ROUTE #167 — a stubbed method call never checks the callee's precondition

**Status: REPAIR DRAFTED by gen #29 (worktree wtN, on top of #166).** Severity 1. Generator: hand
(requires-violation probes after the #165 carrier rerun).

## Measured at `65565510`

    class C:
        #@ requires self.x != 0
        #@ ensures \result == 1
        def get(self) -> int: return self.x // self.x
    #@ ensures \result == 5
    def probe() -> int:  c = C(0); c.get(); return 5      PROVED   (CPython ZeroDivisionError)

The same through a `c: C` parameter, a sibling `self.get(0)` on a param `requires d != 0`, and
`C.get(0)` on a staticmethod: all PROVED. The module-function spelling `get(0)` is refused (control).

Mechanism: `_handle_dotted_call` lowers the call to an abstract `val` (`val c_get_0 () : int`).
Route #70 withholds the callee's POSTCONDITION when it has a `requires` (so the caller cannot
assume it), but nothing carries the PRECONDITION, so the call site discharges nothing. A result
that is discarded (or not needed for the caller's claim) turns a crashing call into a proof.

## Repair (draft)

In `_handle_dotted_call` (trusted), on the abstract-op fallback: resolve the callee's IR name
(`<cls>__<m>`, via route #100's resolution, or `Cls.m` for a class-qualified call; otherwise by
method name over every same-file method) and, when it declares a non-trivial `requires` (route
#70's triviality test), prefix the call with
`assert { [@expl:PyCSL-R167 callee precondition not transmitted to a stubbed method call] false }`.
Fail-closed and local: only reachable call sites are refused. Concrete routes (`sibling_concrete`,
record-array siblings) are untouched and already check the real `requires`.
Witnesses 1569–1572 (XFAIL), 1573 (PASS control).

## Still to measure

Emission census (corpus / pyref / mirrors) before predictions; imported-class methods across files
(multi_file_lib) as a carrier.
