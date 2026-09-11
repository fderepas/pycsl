"""1183 — ROUTE #75 POSITIVE CONTROL: the user's own `ord` contract is reachable.

The true claim about the same program. While the oracle was winning, this did NOT prove --
the call site saw an opaque `ord_op` instead of the user's function.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 9999
#@ assigns \nothing
def ord(c: str) -> int:
    return 9999

#@ ensures \result == 9999
#@ assigns \nothing
def f() -> int:
    return ord("a")
