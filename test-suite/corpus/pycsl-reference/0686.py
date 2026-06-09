"""Test 0686 — negative: `complete` references an undefined act.

`#@ complete b, nope` names `nope`, which is not a defined act. Migrated to
core_ir_semantic._check_acts (Complete/Disjoint referenced names are plumbed). Phase B.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ act b:
#@     given x > 0
#@     ensures \result == 1
#@ complete b, nope
def f(x: int) -> int:
    return 1
