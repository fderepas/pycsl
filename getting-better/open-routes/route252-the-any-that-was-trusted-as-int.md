# OPEN ROUTE #252 — AN `Any` VALUE FLOWING INTO AN `int`-TYPED SLOT IS TRUSTED AS AN INT

**Status: OPEN (gen #36, 2026-10-16), Severity 1.** Residuals of the #251 repair; driver-reproduced at HEAD
6228d5ae (all three rc=0).

## Witnesses (`witnesses-r252/`)
- `r1_any_to_int_param.py`: `g(a: int, b: int)` with `ensures \result == a - b`; `return g(x, x)` for `x: Any`
  proves `\result == 0` (CPython: a user `__sub__` returns 7 — Python does not enforce the annotation).
- `r4_any_into_int_local_annot.py`: same through `int` record fields (`Box(x, x)`; `b.v - b.w`).
- `r3_noexc_any_sub.py`: `#@ no_exception \all` with `y = x - x` on `x: Any` proves; a user `__sub__` can raise.

## Mechanism
Declared-type trust: an `int`-annotated parameter/field/local receives whatever the caller passes; an `Any`
(erased) actual is not checked against the annotation, so #251's uninterpreted arithmetic is bypassed one call
away. `no_exception`: #251 kept `pycsl_py_sub` total, so a raising user dunder is not an exception site.

## Repair direction
(a) Refuse (or require a proof obligation for) an erased/`Any` value flowing into a slot whose type the model
interprets (int/float/str/bool params, fields, annotated locals) — fail-closed at the call/store; measure blast
radius; (b) under `no_exception`, any `pycsl_py_*` operation on an erased operand is an exception site (refuse
or require proof).
