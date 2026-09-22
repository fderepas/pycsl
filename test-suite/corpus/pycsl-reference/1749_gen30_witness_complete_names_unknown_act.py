r"""Test 1749 — WITNESS for `PYCSL-SEM-ACT`: `#@ complete` naming an act that does not exist.

`complete small, nosucharm` claims the listed behaviours cover every case. A name that
matches no `#@ act` makes the claim weaker than it reads — and silently, since the missing
arm contributes nothing to the entry assert. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ act small:
#@     given x < 0
#@     ensures \result == 1
#@ complete small, nosucharm
def f(x: int) -> int:
    return 1
