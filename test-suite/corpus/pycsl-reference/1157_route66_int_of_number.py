"""1157 — ROUTE #66 POSITIVE CONTROL: `int()` of a NUMBER cannot raise and is untouched.

The refusal is keyed on a STRING argument. `int(a)` on an int can never raise `ValueError`,
so it must keep proving — otherwise the fix is a blanket ban on `int()` under a
`no_exception` context and 1156 would pass for the wrong reason.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare

#@ no_exception ValueError
#@ ensures True
#@ assigns \nothing
def f(a: int) -> int:
    return int(a)
