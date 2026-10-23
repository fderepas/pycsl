"""1176 — ROUTE #73 POSITIVE CONTROL: the user's own contract is reachable again.

The same program as 1175, claiming what is TRUE of it (CPython answers -1). This is the
control that makes the repair more than a refusal: while the oracle was shadowing `get`,
this claim did NOT prove either, because the call site saw an opaque `result >= 0` symbol
instead of the user's function. With the oracle refused for a bare call, the real `let` and
its contract are reachable and the true claim discharges.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == d
#@ assigns \nothing
def get(k: str, d: int) -> int:
    return d

#@ ensures \result == -1
#@ assigns \nothing
def f() -> int:
    return get("arity", -1)
