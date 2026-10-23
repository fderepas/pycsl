"""1149 — ROUTE #64 NEGATIVE: `no_exception \all` over an out-of-range byte store.

CPython raises `ValueError: byte must be in range(0, 256)`. This is not excusable as
partial correctness — `no_exception` is a POSITIVE claim about runtime behaviour, `\all`
is its strongest form, and `ValueError` is in `exception_model.KNOWN_EXCEPTIONS`. It
proved before the missing trigger row was added; it must never prove again.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0
#@ no_exception \all
#@ ensures \result == 999
#@ assigns \nothing
def f() -> int:
    b = bytearray([1])
    b[0] = 999
    return b[0]
