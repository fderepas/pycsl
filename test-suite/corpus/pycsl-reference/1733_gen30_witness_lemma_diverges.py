r"""Test 1733 — WITNESS: a `#@ lemma` may not also be `#@ \diverges`.

A non-terminating "proof" proves anything, which is why this one is a hard error rather
than a weaker verdict. Sibling of 1731 (returns a value) and 1732 (carries a frame).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ lemma
#@ \diverges
#@ ensures 2 + 2 == 4
def triv() -> None:
    pass
