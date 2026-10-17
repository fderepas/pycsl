# OPEN ROUTE #258 — `Optional[Any]` / `Any | None` IS LOWERED WITH ONLY THE `None` ARM

**Status: OPEN (gen #36, 2026-10-17), Severity 1.** Residual of the #254/#255 repair; driver-reproduced at
HEAD 6f8937b1: `u_Optional_Any__.py` and `u_Any___None_.py` rc=0 (CPython 6, claim `\result == 5`).

## Witness (`witnesses-r258/u_Optional_Any__.py`)
    def f(x: Optional[Any]) -> int:     # ensures \result == 5   <-- PROVED
        if x is not None:
            return 6
        return 5
Siblings: `Any | None`, `Optional[object]`, `Union[Any, None]`, `Union[int, Any]` (check each).

## Mechanism
Module 5 `_normalize_union_annotation` drops the `Any` arm (GT1); `core_ir_semantic` only warns. The parameter
becomes a union whose only inhabitant is `None`, so `x is not None` is dead in the model.

## Repair direction
A union containing `Any`/`object` (or an unknown arm) must lower to an erased value (Any) — never drop the arm;
or refuse. Measure corpus/mirror blast radius of the normalization change (M1).
