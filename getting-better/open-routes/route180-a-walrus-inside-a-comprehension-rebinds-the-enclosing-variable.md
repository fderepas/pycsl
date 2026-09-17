# ROUTE #180 — a walrus inside a comprehension rebinds the enclosing variable; the model keeps the old value

**Status: REPAIR DRAFTED by gen #29 (worktree wtAA, branch wip/g29-r180, on top of #179).** Severity 1.
Generator: hand (assignment-expression scope probes after #177).

## Measured at `ad627c49`

    #@ ensures \result == 0
    def probe() -> int:
        y = 0
        xs = [(y := x) for x in [1, 2, 3]]
        return y                                   PROVED   (CPython 3)

    last = 0; t = sum((last := x) for x in [1, 2, 3]); return last     PROVED `== 0` (CPython 3)

PEP 572 binds a walrus target inside a comprehension or generator in the CONTAINING function. The
comprehension lowers to an opaque `list_comp 0` value, so the rebinding vanishes. Refused at HEAD:
walrus in a while condition, walrus behind a short-circuit, walrus inside `any()`; mutating method /
helper calls inside a comprehension.

## Repair (draft)

`_reset_function_state` (trusted): a `NamedExpr` anywhere inside a ListComp / SetComp / DictComp /
GenExp is refused, unconditionally. Branch also carries a doc-only fix: `test-suite/annotations.md`
§7.1 claimed a Python `assert` lowers to `check { ... }`; the emitter lowers it to `()` (translational
reference §T.5.8, README, static semantics all agree) — corrected.

Emission byte-inert (corpus/pyref/mirrors). Witnesses 1636, 1637 (XFAIL), 1638 (PASS: walrus in a plain
condition). Fast planes 19/19, conformance, sync, doc-coherency green.
