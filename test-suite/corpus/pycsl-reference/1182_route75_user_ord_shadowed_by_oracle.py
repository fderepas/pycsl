"""1182 — ROUTE #75 NEGATIVE: a user function shadowing a builtin must not lose to its oracle.

Python lets a module shadow a builtin. When it does, `_call_named_builtins`' name tests fired
on the USER'S function and handed the call `val ord_op` with `ensures { 0 <= result < 256 }` --
an AXIOM about the BUILTIN's behaviour, asserted about a function the user wrote and proved.
CPython answers 9999. Anti-vacuity is carried by 1183.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 9999
#@ assigns \nothing
def ord(c: str) -> int:
    return 9999

#@ ensures \result < 256
#@ assigns \nothing
def f() -> int:
    return ord("a")
