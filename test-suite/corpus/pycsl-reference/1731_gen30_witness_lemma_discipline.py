r"""Test 1731 — WITNESS for the `PYCSL-SEM-LEMMA` family, which had none.

A `#@ lemma` is a PROOF, not a computation, and the compiler enforces four things about
one: it must state a fact (`#@ ensures`), it must be `-> None`, it must be
`assigns \nothing`, and it may not be `#@ \diverges` (a non-terminating lemma proves
anything). Three of those five raise sites were UNWITNESSED — measured by
`bin/check-refusal-witness-coverage.py`, which found 140 of the compiler's 198 refusals
with no file proving they can fire.

This file takes the RETURN-A-VALUE arm: a lemma whose body returns an int. Its siblings are
1732 (a lemma carrying a frame) and 1733 (a lemma that also declares `\diverges`).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ lemma
#@ ensures 2 + 2 == 4
def triv() -> int:
    return 1
