"""1153 — ROUTE #65 POSITIVE CONTROL: a WIRED trigger row still discharges.

The repair refuses constructs whose trigger rows are orphaned; it must not damage the rows
that work. A guarded division under `no_exception ZeroDivisionError` goes through the LIVE
`("binop", ...)` row and must keep proving — otherwise the fix is a blanket ban on
`no_exception` and 1151/1152 would pass for the wrong reason.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare

#@ no_exception ZeroDivisionError
#@ requires b != 0
#@ ensures True
#@ assigns \nothing
def f(a: int, b: int) -> int:
    return a // b
