# ROUTE #148 — an UNANNOTATED float literal stored in a field is TRUNCATED to an int

**Status: CLOSED AND FULLY GATED by gen #29 (2026-09-16), battery D (with #149). Witnesses 1480 1483 1484 1485 (XFAIL), 1490 (PASS on both).** Severity 1. Generator: carrier-rerun
(gen #27's WATCH row on its own #139 `field_defaults` arm).

## The defect

Every `field_defaults` collector accepts `isinstance(value, (int, float))` and records
`int(value)`. For an UNANNOTATED field the record type is `int`, so `self.r = 2.5` becomes the
record literal `{ r = 2 }` — a DEFINITE WRONG value, not an unknown one.

## Measured at `acba66f3` (CPython contradicting)

    class Cy:
        def __init__(self) -> None:
            self.r = 2.5
    c = Cy(); if c.r > 2: return 1; return 0      #@ ensures \result == 0   <-- PROVED; CPython 1

LIVE spellings (`scratchpad/g29/cr/`): the first store `f3`, a last-wins second store `f8`
(route #88's arm), a keyword-only constructor default `def __init__(self, *, r: float = 2.5)` `f7`
(route #82's `kwonly_defaults`). FAIL-CLOSED: every ANNOTATED `float` spelling (the field is
typed `real` and the truncated int default is a Why3 type error — `f5` `f6` `f9` `f10`); a
negative literal `-2.5` (#139 marks the UnaryOp unknown — `f13`); a read through a METHOD (the
call lowers to an abstract `val` — `f1`).

## Sites (all `int(<float>)`)

`Module5_IREmitter.py` ~2872 (class-body N1b), ~3219 (first store), ~3291 (annotated store),
~3343 (#88 last-wins), ~3471 (dataclass class body); `module5/construction_synth.py` ~230
(kw-only defaults), ~582/586 (`_dc_default_const`). Route #79's `_lit79` exemption treats every
`ast.Constant` as "carried faithfully by field_defaults", so simply skipping the float would fall to
the definite witness 0 — the exemption must stop covering a non-integral float too.

## Scoped repair (not landed)

Accept an `int` (not bool-special-cased beyond today) or an INTEGRAL float only; a non-integral
float is not a `field_defaults` value, and #79 marks it UNKNOWN. Census the float literals in
field stores across both corpora, the mirrors, `src/pycsl` and `src/pycsl_lib` before predicting.

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
