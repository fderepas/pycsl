# OPEN ROUTE #253 — A BUILTIN-ANNOTATED VALUE MAY BE A SUBCLASS INSTANCE WITH OVERRIDDEN DUNDERS

**Status: OPEN (gen #36, 2026-10-16), Severity 1, design-level.** Residual of the #252 repair (reproducer
`scratchpad/r252/res/res_intsub.py` in the executor's scratch; restated here).

## Witness
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(x: int) -> int:
        return x - x
PROVES; CPython `f(I(5))` = 7 for `class I(int): def __sub__(s, o): return 7`.

## Mechanism
The model treats a value annotated `int` / `float` / `str` / `bool` / ... as an EXACT builtin instance:
its arithmetic/comparison/equality are the builtin's. Python allows subclass instances with overridden dunders
wherever the base type is accepted (and type checkers accept them).

## Repair direction (design decision)
Fail-closed is not viable (every typed program would lose its arithmetic). Precedent: `HASH-EQ-CONSISTENCY`
(a REVIEWED ASSUMPTION surfaced by `bin/check-assumed-facts.py` with a `--strict-hash-eq-consistency` mode).
Treat "builtin-annotated values are exact builtin instances (no dunder-overriding subclass)" and route #250's
"floats are finite and non-NaN" the same way: a NAMED, SURFACED model assumption in `--soundness-report`
and the reference docs, plus (where feasible) a `--strict-*` mode that drops it.
