"""Test 1006_route29_array_eq_typed_erasure — ROUTE #29 negative witness: `\array_eq` under `--memory-model typed`.

FALSE OF THE PROGRAM: `a` becomes [1,1] and `b` becomes [9,9], and the two
regions are `\separated`, so they are not element-wise equal.

BEFORE relaunch #45 this file printed `[+] Verification SUCCESS! All contracts
formally proven.` — `module6_whyml/expressions.py` lowers the atom as
`if self._value_semantic: <real formula>` with a fall-through literal, and
`_value_semantic` is `memory_model in ("hoare", "concurrent")`, so the whole
typed/store family emitted `ensures { true }` (or `= 0` for `\sum`).
The pipeline now REFUSES the atom under a heap model
(`PYCSL-R29-HEAP-SPEC-ERASURE`), so this must never verify again.
"""
# pycsl-flags: --memory-model typed
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires \valid(a, 2)
#@ requires \valid(b, 2)
#@ requires \separated(a, 2, b, 2)
#@ ensures \array_eq(a, b)
#@ ensures \result == 0
def f(a: list, b: list) -> int:
    a[0] = 1
    a[1] = 1
    b[0] = 9
    b[1] = 9
    return 0
