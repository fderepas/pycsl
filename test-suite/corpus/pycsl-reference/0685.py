"""Test 0685 — negative: `\result` in an act `given` guard.

`given` guards are evaluated in the pre-state, so `\result` is not allowed. Migrated to
core_ir_semantic._check_acts (the Act's given-guard exprs are plumbed). Phase B.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ act b:
#@     given \result == 0
#@     ensures \result == 1
def f(x: int) -> int:
    return 1
