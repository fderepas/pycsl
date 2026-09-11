"""1163 — ROUTE #68 NEGATIVE: `1 << -1` under `no_exception \all`.

CPython raises `ValueError: negative shift count`. The `("binop","<<")` row has carried
`non_neg_shift` ALL ALONG — it was simply never injected, because the bitwise/power emission
path did not wrap while `div`/`mod` did. A row that exists and is not consulted is a
soundness claim that is never checked.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    return 1 << (-1)
