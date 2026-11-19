# ROUTE #186 — the `raises` wrap's key mis-resolves a field receiver, so a declared `raises` is never discharged

**Status: CLOSED by gen #29 (battery Z green: suite 3786/3804, the same 18 CONFIRMED FAIL, zero XPASS; planes --slow 34/34).**
Severity 1.
Generator: carrier-rerun of the landed #185 (the same mis-keying, one consumer further).

## Measured at `8a30d42f`

    class Inner:
        #@ raises ValueError when v < 0
        def go(self, v: int) -> int:
            if v < 0: raise ValueError()
            return v
    class Outer:
        #@ no_exception ValueError
        #@ ensures \result == 0
        def run(self) -> int:  self.inner.go(-1); return 0     PROVED   (CPython ValueError)

The local-receiver spelling (route #105) is refused. Route #185 repaired the key that routes
#167/#176 use; the key handed to `_wrap_call_with_callee_raises_assert` is computed in the same block
and still resolved `self.inner.go` to `outer__inner_go` — a name no function carries — so the wrap
found no `raises` and emitted no `assert { not P }`.

## Repair

An unmatched key falls back to the method-name match: ONE candidate resolves it; several candidates
that can raise leave it unresolved and the call carries an `assert { false }` under an active
`no_exception` context (attaching one class's condition to another's callee would be a WRONG fact).
Two emission-hygiene fixes ride along, both measured: the route #167 precondition rendering left a
dead `val constant pycslrsixseven0x` behind, and `_render_callee_condition` registered
`val constant 1 : int` for a literal actual under `subst` — a Why3 SYNTAX error that failed the whole
file (it is why the first draft's own PASS control failed). Emission: 6 corpus files MOVED (four
XFAIL that now carry a rendered condition or lose the dead `val`; 0522 and 1614 are PASS and still
prove), pyref and mirrors byte-inert. Witnesses 1658, 1659 (XFAIL), 1660 (PASS). Fast planes 19/19,
conformance, sync green.
