# ROUTE #169 — the global-method inliner lets caller locals capture the spliced body's names

**Status: REPAIR DRAFTED by gen #29 (worktree wtP, on top of #168).** Severity 1. Generator: hand
(inliner capture probes following #168).

## Measured at `dc4520d4`

    K = 3
    class C: def f(self) -> int: return K
    _g = C(0)
    #@ ensures \result == 9
    def probe() -> int:  K = 9; return _g.f()          PROVED   (CPython 3)

    class C: def f(self, d): a, b = d, d; return a + b
    #@ ensures \result == 100
    def probe() -> int:  a = 7; _g.f(100); return a     PROVED   (CPython 7)

`frontend/ir_inline.py` splices the callee body into the caller. Only the callee's single-name
`Assign`/`AugAssign`/`For` targets were freshened: a name the callee reads from module scope, and
a tuple-unpack target, kept their spelling and resolved to (or overwrote) the caller's local.
Controls (correct at HEAD): a callee local assigned by `=`, a `for i in range` target, a formal
rebound in the body, a non-trivial actual with a global mutator call.

## Repair (draft)

In `_Inliner._expand` (trusted stub in the mirror — `_assigned_locals`/`_substitute` are verified
mirror bodies and were left untouched, since the mirror emission of a `targets` loop does not type):
tuple-unpack targets are added to the freshening map and the `targets` lists renamed after
substitution; then every unfreshened identifier of the spliced body (Var names, `target`/`object`
strings, `targets` items, dotted-call receivers) that the caller binds (parameters, any
`target`/`targets` of a statement, recomputed per fixpoint round in `_inline_calls`) is refused with
a PyCSLSemanticError naming route #169. Emission: corpus/pyref/mirrors byte-inert.
Witnesses 1578, 1579 (XFAIL), 1580 (PASS control, FAILS at HEAD). Fast planes 19/19,
conformance 38/38 + 38/38, sync rc=0.

## Known completeness loss

A comprehension variable in the callee named like a caller local (`[i * 2 for i in range(n)]`
with caller `i = 7`) is refused although Python scopes it (hand-measured, h10); 0 corpus sites.
