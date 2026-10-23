r"""Test 1747 — WITNESS: a `#@ lemma` that states nothing.

"a lemma must state the fact it proves" — one with no `#@ ensures` is a proof of nothing
wearing the word lemma. Completes the lemma family alongside 1731 (returns a value), 1732
(carries a frame) and 1733 (also `\diverges`).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ lemma
def triv() -> None:
    pass
