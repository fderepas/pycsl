"""1173 — ROUTE #72 NEGATIVE: `str.split("")` under `no_exception \all`.

CPython raises `ValueError: empty separator`. There is no trigger row for `split`, and the
separator is HASHED TO AN INT before it reaches an opaque `val s_split_1 (x0: int) : int`,
so no faithful obligation can be injected — refused rather than discharged.

Seventh carrier of ONE defect: nothing relates the trigger table to the operations the
emitter actually EMITS.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    s = "ab"
    parts = s.split("")
    return 0
