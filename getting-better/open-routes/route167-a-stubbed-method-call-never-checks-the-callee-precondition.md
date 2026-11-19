# ROUTE #167 — a stubbed method call never checks the callee's precondition

**Status: CLOSED by gen #29 (battery M green: suite 3708/3726, same 18 CONFIRMED FAIL, zero XPASS; planes --slow 34/34).** Severity 1. Generator: hand
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

## Repair (draft 2)

Draft 1 asserted `false` at every such call: emission census moved 10 corpus files and broke six
PASS programs (0452 0522 0721 0967 1286 1293) whose preconditions DO hold. Draft 2, in
`_handle_dotted_call` (trusted), on the abstract-op fallback: resolve the callee's IR name
(`<cls>__<m>` via route #100's resolution, or `Cls.m`; otherwise by method name over every
same-file method), and for each non-trivial `requires` (route #70's triviality test) assert the
clause at the call site — rendered in spec context with the parameters renamed to placeholders IN
THE IR (a `subst` map missed `\length(data)`), `self` replaced by the named receiver, then the
placeholders replaced by the call's arguments. Anything not faithfully renderable (unresolved
callee, missing argument, a receiver that is not a name, a leftover parameter/`self` token)
asserts `false`. Label `PyCSL-R167 callee precondition at a stubbed method call`.

Emission (vs battery L candidate): corpus 10 MOVED (exactly the calls to guarded methods), 0 GONE;
pyref and mirrors byte-inert. The six PASS programs prove again; the four XFAIL programs still fail.
Carriers (hand, draft): kwarg call and chained `h.c.sget()` assert false; receiver named `d`,
subclass instance, field reassigned after construction, call-valued argument all refused.
Witnesses 1569–1572, 1574 (XFAIL), 1573 (PASS control, non-vacuous).
Fast planes 19/19 (after removing a `finally` that broke the TRYFINAL ratchet and making 1573
non-vacuous), conformance 38/38 + 38/38, sync rc=0, mirror-coverage 549/41.

## Carrier folded in (wtP)

`C(0).sget()` and `super().sget()` reach the generic unannotated-call fallback (bare method name,
`receiver` field) and still PROVED on draft 2. That fallback now asserts false when a same-file
method of that name has a non-trivial precondition. Corpus/pyref/mirrors byte-inert.
Witnesses 1581–1582 (XFAIL). Landing: with #168/#169 as `wip/g29-r166..wip/g29-r169`.

## Still to measure

Emission census (corpus / pyref / mirrors) before predictions; imported-class methods across files
(multi_file_lib) as a carrier.
