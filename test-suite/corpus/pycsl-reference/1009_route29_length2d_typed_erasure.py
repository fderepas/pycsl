"""Test 1009 — ROUTE #29 PIN: `\length2d` under `--memory-model typed`.

FALSE OF THE PROGRAM: the precondition declares `mat` to be 2x2 and the
postcondition claims the same matrix is 99x99.

THIS IS A PIN, NOT A FLIP WITNESS, and the difference is stated rather than
buried. `_handle_length2d_expr` has the identical route-#29 shape
(`if self._value_semantic: <formula>` ... `return "true"`), so under a heap model
the postcondition emitted as `ensures { true }` — but at the parent commit
c4233fed this file did NOT prove: it died on `unbound type symbol 'matrix'`,
because the emitter puts a `matrix`-typed declaration into a typed-model module
that never pulls the theory. That is fail-closed BY ACCIDENT — the same accident
that masked `\sum` (1008), and the same bug class relaunch #44 fixed once for
abstract ops. A completeness fix to the `use` could make it live at any time.
The pipeline now REFUSES the atom under a heap model
(`PYCSL-R29-HEAP-SPEC-ERASURE`); this file pins that refusal in place.
"""
# pycsl-flags: --memory-model typed
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires \length2d(mat, 2, 2)
#@ ensures \length2d(mat, 99, 99)
#@ ensures \result == 0
def f(mat: list) -> int:
    return 0
