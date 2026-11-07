"""1160 — ROUTE #67 NEGATIVE: a STRING subscript read out of range.

CPython raises `IndexError: string index out of range`. The ARRAY read was wired all along
(`in_bounds (Array.length a) i`); the STRING read went down the `char_code_at` path that no
trigger row covered, and `val char_code_at` asserts its postconditions UNCONDITIONALLY in
`i` — a totality Python does not have. Proved before the row was wired.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    s = "ab"
    return ord(s[5])
