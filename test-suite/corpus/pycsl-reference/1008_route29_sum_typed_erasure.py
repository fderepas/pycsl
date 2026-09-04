"""Test 1008_route29_sum_typed_erasure — ROUTE #29 negative witness: `\sum` under `--memory-model typed`.

FALSE OF THE PROGRAM: `\sum(arr, 0, 3)` over [1,2,3] is 6, and this returns 0.
This one was masked at the parent commit by an UNRELATED L3 type error — the
`pycsl_sum` helper needs `array int` and the typed-model module has no
`use array.Array` — i.e. fail-closed BY ACCIDENT, on exactly the bug class
relaunch #44 already fixed once for abstract ops. The emission was
`ensures { (result = 0) }` on a function whose body is `0`.

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
#@ requires \valid(arr, 3)
#@ requires arr[0] == 1
#@ requires arr[1] == 2
#@ requires arr[2] == 3
#@ ensures \result == \sum(arr, 0, 3)
def f(arr: list) -> int:
    return 0
