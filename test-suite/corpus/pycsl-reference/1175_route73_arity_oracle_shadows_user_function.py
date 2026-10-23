"""1175 — ROUTE #73 NEGATIVE: an opaque oracle must not shadow a user-defined function.

`_lower_dict_get_call` fired on ANY two-argument call named `get` whose first argument was
the literal string "arity", and replaced it with `val get_arity_field ... ensures
{ result >= 0 }`. Here `get` is a FUNCTION THE USER DEFINED, with its own proved contract
`ensures \\result == d`. CPython answers -1. Before the fix, `\\result >= 0` PROVED — a
false postcondition about ordinary TOTAL Python, needing no `no_exception` and no opt-in of
any kind.

ANTI-VACUITY is carried by 1176: the TRUE claim about this same program PROVES, so this
driver does not fail merely because nothing about it is provable.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == d
#@ assigns \nothing
def get(k: str, d: int) -> int:
    return d

#@ ensures \result >= 0
#@ assigns \nothing
def f() -> int:
    return get("arity", -1)
