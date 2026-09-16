# ROUTE #149 — an OMITTED positional constructor argument ignores the parameter's DEFAULT

**Status: OPEN. Found and reproduced by gen #29 (2026-09-16).** Severity 1. Generator: carrier-rerun
(while probing route #148's float family). The positional twin of route #82.

## Measured at `acba66f3` (CPython contradicting)

    class Cy:
        def __init__(self, r: int = 5) -> None:
            self.r = r
    c = Cy(); if c.r > 2: return 1; return 0      #@ ensures \result == 0   <-- PROVED; CPython 1

The record literal is `{ r = 0 }`: `field_defaults` is `{'r': 0}` and `init_params` is `['r']`,
but the IR carries NO positional parameter defaults (`__init__` is not in `functions`, so
`param_defaults` never reaches Module 6). `Cy(5)` is faithful (`f15`). The float spelling
`r: float = 2.5` gives the same `{ r = 0 }` (`f11`).

## The deferral that hides it

`_call_record_constructor`'s docstring: "a field WITH a default whose arg is OMITTED keeps that
default (WL-07)". True for a `@dataclass`, where the FIELD default IS the parameter default; false
for an explicit `__init__`, where the parameter default is a separate value and the field's
"default" is the collector's witness. Also the whole binding block is guarded by `(args and ...)
or kwargs_map or kwonly_defaults`, so a ZERO-argument `C()` binds nothing at all.

## Scoped repair (not landed)

Module 5 emits `init_param_defaults` (positional parameter -> constant int default) ONLY when
non-empty (census the 38 frozen conformance goldens first — they must not carry it); Module 6 seeds
omitted positional parameters from it, exactly like route #82's keyword-only seeding, and a
parameter with a NON-constant default whose argument is omitted makes every field it initialises
UNKNOWN. Census constructor calls that omit a defaulted positional argument over both corpora and
the mirrors, and PREDICT the moved emission set before the sweep.
