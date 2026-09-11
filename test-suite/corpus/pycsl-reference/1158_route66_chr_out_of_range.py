"""1158 — ROUTE #66 NEGATIVE: `chr(n)` outside [0, 0x110000) under `no_exception \all`.

CPython raises `ValueError: chr() arg not in range(0x110000)`. There was no trigger row, and
worse, the abstract `chr_op` carried `ensures { String.length result = 1 }` UNCONDITIONALLY
— asserting a TOTALITY Python does not have. Proved before the row was wired.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    return len(chr(-1))
