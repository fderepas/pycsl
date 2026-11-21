"""Test 1050 — ROUTE #43 negative witness (a): a COMPLEX literal was the integer zero.

FALSE OF THE PROGRAM: `3j == 0` is False in Python, so this returns 0.

`_py_expr_constant` lowers `isinstance(expr.value, complex)` to
`{"type": "Number", "value": int(expr.value.real)}` — the imaginary part is DISCARDED and
the real part is TRUNCATED TO AN INT. There is no complex model anywhere in the pipeline,
so what the model receives is an ordinary integer that every comparison then decides on.
At the parent commit f2873419 this proved `\result == 7`.

THE WINDOW'S GENERAL SHAPE A FOURTH TIME (after `...`, the `Ellipsis` name and the
recorded `None` residue): a Python value the model cannot represent, lowered to an INTEGER
LITERAL, is not merely lost — it is DECIDABLE, and decided wrongly.

REFUSED rather than made opaque, and the reason is a measurement rather than a taste: the
whole tree contains exactly ONE complex literal (`python-reference/0044`, an assert-only
coverage driver, now `pycsl-expected: FAIL`), so opacity would buy no program anything
while a refusal says the true thing — PyCSL models no complex arithmetic at all, and
`c.real` / `c.imag` are not modelled either.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = 3j
    if x == 0:
        return 7
    return 0
