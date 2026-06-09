"""Test 0684 — negative: duplicate act name.

`_validate_acts` rejects two `#@ act` blocks with the same name. Now checked on the IR
(core_ir_semantic._check_acts via the plumbed `acts` field). Characterization test for
the IR migration (Phase B / AST-only).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ act b:
#@     given x > 0
#@     ensures \result == 1
#@ act b:
#@     given x <= 0
#@     ensures \result == 0
def f(x: int) -> int:
    return 1
