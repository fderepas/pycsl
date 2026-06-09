"""Test 0688 — negative: `\result` used outside `ensures`.

`\result` is bound only at return, so it is allowed only in `ensures` — here it is in a
`requires`. Migrated to core_ir_semantic._check_contract_scope (the `allow_result` flag
is true only for ensures). Characterization test for the IR migration (Phase B).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires \result > 0
def f(x: int) -> int:
    return x
