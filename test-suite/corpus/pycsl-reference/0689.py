"""Test 0689 — negative: undefined variable referenced in a contract.

`nope` is not a parameter or module constant. Migrated to
core_ir_semantic._check_contract_scope (free-variable extraction ported as
`_ir_free_vars`). Characterization test for the IR migration (Phase B).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires nope > 0
def f(x: int) -> int:
    return x
