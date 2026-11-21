"""Test 1005_route29_is_sorted_store_erasure — ROUTE #29 negative witness: `\is_sorted` under `--memory-model store`.

FALSE OF THE PROGRAM: the store-model twin of 1004 — the body writes 3, 2, 1
and the postcondition claims the region is sorted ascending.

BEFORE relaunch #45 this file printed `[+] Verification SUCCESS! All contracts
formally proven.` — `module6_whyml/expressions.py` lowers the atom as
`if self._value_semantic: <real formula>` with a fall-through literal, and
`_value_semantic` is `memory_model in ("hoare", "concurrent")`, so the whole
typed/store family emitted `ensures { true }` (or `= 0` for `\sum`).
The pipeline now REFUSES the atom under a heap model
(`PYCSL-R29-HEAP-SPEC-ERASURE`), so this must never verify again.
"""
# pycsl-flags: --memory-model store
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires \valid(arr, 3)
#@ ensures \is_sorted(arr, 0, 3)
#@ ensures \result == 0
def f(arr: list) -> int:
    arr[0] = 3
    arr[1] = 2
    arr[2] = 1
    return 0
