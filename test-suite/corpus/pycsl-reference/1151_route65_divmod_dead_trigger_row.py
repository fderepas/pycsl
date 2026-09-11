"""1151 — ROUTE #65 NEGATIVE: a trigger row the emitter never looks up.

`exception_model.TRIGGERS` carries `("call", "divmod") -> no_div_zero({1})` — a REAL
condition, correctly written. No emitter site ever passes that op-key, so the obligation
was never injected and this proved while CPython raises ZeroDivisionError.

The contrast that makes it crisp: `d[5]` under `no_exception KeyError` does NOT prove,
through the `("map_get", None)` row, which IS wired. Same machinery, same exception family.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare

#@ no_exception ZeroDivisionError
#@ ensures True
#@ assigns \nothing
def f(a: int) -> int:
    q = divmod(a, 0)[0]
    return q
