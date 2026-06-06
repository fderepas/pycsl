"""Test 0561 — negative: a lemma with a false `#@ ensures` fails (body can't prove it).

`false_lemma` claims `1 == 2`; the (empty) proof body cannot discharge it, so Why3
rejects the postcondition. A lemma introduces NO axiom that isn't itself checked
(lemma.md §2/§7.1) — a false claim is a hard verification failure, not an assumed
fact. Negative twin of the non-recursive flagship 0558.

Committed `# pycsl-expected: FAIL` and STAYS failing.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ lemma
#@ ensures 1 == 2
#@ assigns \nothing
def false_lemma() -> None:
    pass
