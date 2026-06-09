"""Test 0682 — negative: positional mutable default argument.

`def f(acc=[])` — a list/dict/set default is shared across calls (ownership R2). Now
checked on the IR (core_ir_semantic._check_mutable_defaults via the front-end-resolved
`has_mutable_default` flag). Characterization test for the IR migration (Phase B).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 0
def f(acc=[]) -> int:
    return 0
