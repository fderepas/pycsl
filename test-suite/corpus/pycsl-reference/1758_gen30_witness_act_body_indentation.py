r"""Test 1758 — WITNESS: an `#@ act` body indented by something other than four spaces.

The act block's body must be indented EXACTLY four spaces under its header; anything else
is refused rather than guessed at, because a mis-read block boundary silently changes which
clauses belong to which behaviour. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness. Sibling: 1755 (a
tab).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ act small:
#@   given x < 0
#@   ensures \result == 1
#@ complete small
def f(x: int) -> int:
    return 1
