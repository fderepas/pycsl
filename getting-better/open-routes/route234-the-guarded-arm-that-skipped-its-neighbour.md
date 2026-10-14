# ROUTE #234 — THE GUARDED CONSTRUCTOR ARM THAT SKIPPED ITS NEIGHBOUR

**Status: REPAIRED (gen #36, 2026-10-14), Severity 1.** Found by the route #233 executor while
probing guarded `match` shapes (same `match` lowering, different mechanism: arm order, not binding).

## Witness (PROVED at 87ff222f; CPython returns 2)
`test-suite/corpus/pycsl-reference/1996_gen36_ctor_guard_fallthrough_skips_arm_refused.py`:

    #@ datatype Maybe = MNone | MSome(int)
    #@ ensures \result == 7
    def f() -> int:
        r = 7
        o = MSome(-5)
        match o:
            case MSome(n) if n > 0: r = 1
            case MSome(n):          r = 2
            case MNone():           r = 3
        return r

## Mechanism
A `match` with a constructor arm lowers to Why3's native `match`, whose arms cannot carry a
guard. A guarded arm became `<pat> -> if g then <body> else <fall-through>`, where the
fall-through is the body of the FIRST wildcard arm, or `()` when there is none
(`stmt_control_flow._handle_match_stmt`). Every arm BETWEEN the guarded arm and the wildcard is
skipped: here the failed guard on `MSome(-5)` fell to `()` and `r` stayed 7. A guarded wildcard
was also used as the fall-through with its own guard ignored.

## Repair landed (gen #36, 2026-10-14, with route #233)
Module 5 `_build_function_ir` (inline, mirror-`\trusted`): in a `match` that has a constructor
arm (top-level or inside an or-pattern — exactly the native-lowering trigger), a guarded arm is
accepted only when it is the LAST arm or is followed DIRECTLY by an unguarded `case _:` (the two
cases where the fall-through IS Python's next arm); every other guarded arm, and every guarded
wildcard, is refused fail-closed (`[ir-emit] ... route #234`). The if-chain lowering (no
constructor arm) threads guards faithfully and is untouched. Census: one guarded constructor arm
in either corpus (`pycsl-reference/0531`, followed by `case _:`, still VERIFIES); 0 in the mirror.
Witness 1996 PROVED at 87ff222f, refused now.

## Residue
A faithful lowering (nest the remaining arms as the `else` of the guard) is not built; the
refusal names the two supported placements.
