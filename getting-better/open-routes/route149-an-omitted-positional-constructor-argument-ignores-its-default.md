# ROUTE #149 — an OMITTED positional constructor argument ignores the parameter's DEFAULT

**Status: CLOSED AND FULLY GATED by gen #29 (2026-09-16), battery D (with #148). Witnesses 1477-1483 1491 (XFAIL), 1486-1489 1492 (PASS). Extra witnesses 1511/1512 travel with battery E.** Severity 1. Generator: carrier-rerun
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

## Closed (gen #29, battery D — every leg predicted and hit)

Repair: `construction_synth._collect_init_construction` captures every parameter default of either
kind — an int, a bool, an integral float or a folded negative literal — into `init_param_defaults`
(positional, new popped-free IR key emitted only when non-empty) or the existing
`init_kwonly_defaults`, and lists every other defaulted parameter in `init_default_unknown`;
`_call_record_constructor` seeds omitted positional arguments, marks fields initialised from an
omitted unknown-default parameter UNKNOWN (int/bool-typed fields), parenthesizes negative splices,
and enters the binding block for a zero-argument call when defaults exist. The #147 inherit copy
carries both keys. A non-integral float literal store is no longer a `field_defaults` value and
route #79 no longer exempts it.
Battery D: emission vs the #143-closed tree 1125 -> 1141 0/0/0, python-reference and mirrors inert;
conformance 38/38 + 38/38; suite 3618/3636 same 18, zero XPASS; planes --slow 34/34.
