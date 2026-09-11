# OPEN ROUTE #65 — THE `.index` `ValueError` TRIGGER IS THE LITERAL STRING `"true"`,
# SO IT DISCHARGES UNCONDITIONALLY
# (found 2026-09-11 by relaunch #55, at `962682e9`, one probe after route #64)

## THE HEADLINE

```python
#@ no_exception ValueError        # and `#@ no_exception \all` — both prove
#@ ensures True
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2]
    return xs.index(5)            # CPython: ValueError: 5 is not in list
```

**`[+] Verification SUCCESS! All contracts formally proven.`**

## IT IS WORSE THAN A MISSING ROW, AND THAT IS THE POINT

Route #64 was a MISSING trigger row. This one is PRESENT — in
`src/pycsl/exception_model.py`:

```python
    ("attr_call", "index"):   [("ValueError", "true")],  # placeholder; \mem when proof needs it
```

The second element of a trigger is the WhyML condition that must hold for the operation NOT
to raise. Here it is the literal `true`, so the injected obligation is `assert { true }`,
which discharges for every program. **A missing row at least does not claim to cover the
case; a `"true"` row makes the table look complete while covering nothing.** The source
comment says "placeholder" and is honest about it — nothing downstream is.

**MEASURED TO HAVE ZERO DISCRIMINATION**, which is the crisp statement of the defect:

  * `xs.index(5)` — element ABSENT, CPython raises — **PROVES**.
  * `xs.index(1)` — element PRESENT, CPython does not raise — **PROVES**.

Identical verdicts. The row cannot tell the two apart, so it contributes nothing to any
`no_exception` proof that mentions `ValueError`.

## THE MECHANISM IS NOT BROKEN — SAME CONTROL AS ROUTE #64

`a // 0` under `#@ no_exception ZeroDivisionError` does NOT prove; `a // b` with
`requires b != 0` DOES. The injection machinery discharges real obligations. This row simply
hands it a tautology.

## ALSO CHECKED, AND NOT A FINDING

  * `("call", "next"): [("StopIteration", "true")]` is the same shape, but an explicit
    `next(iter(xs))` is not expressible (type error), so the row is unreachable today. It
    should still be fixed when `next` lowers — it is the identical trap.
  * A `for` loop over an EMPTY list under `no_exception \all` proves, and that is CORRECT:
    Python's `for` consumes `StopIteration`, it does not propagate it. Recorded so a future
    probe does not mistake it for a route.

## THE REPAIR SHAPE

Replace `"true"` with a real membership condition over the receiver — the source comment's
own `\mem` suggestion. The trigger template takes positional operands, so the call site must
supply the receiver array and the searched value, and the condition becomes "the value occurs
in the array". If a faithful membership term is not available for every receiver shape, the
honest fallback is to REFUSE `.index` under a `ValueError` `no_exception` context rather than
to discharge it — a refusal is the safe direction, a tautology is not.

## THE GENERAL LESSON, WHICH IS BIGGER THAN THIS ROW

**A TRIGGER TABLE IS A SOUNDNESS CLAIM PER ROW, AND A PLACEHOLDER ROW IS A FALSE ONE.**
Anything that reads like coverage — a row, a case arm, a registered handler — should be
checked for whether it DISCRIMINATES, not merely whether it exists. The test is cheap: run
the safe case and the raising case and confirm the verdicts DIFFER.
