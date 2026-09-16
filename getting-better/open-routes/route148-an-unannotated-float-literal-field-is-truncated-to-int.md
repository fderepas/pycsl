# ROUTE #148 — an UNANNOTATED float literal stored in a field is TRUNCATED to an int

**Status: OPEN. Found and reproduced by gen #29 (2026-09-16).** Severity 1. Generator: carrier-rerun
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
