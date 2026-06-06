"""Test 0571 — negative: a plain lemma may not rest on a \trusted fact (trust-leakage).

`leaky`'s body calls `opaque`, a `#@ \trusted` (unverified) function. A `#@ lemma` is a
CHECKED fact; letting its proof rest on a trusted (assumed) value would smuggle an
unverified axiom into a "proved" lemma. Why3 CANNOT catch this (the trusted `val`'s
contract is axiomatic), so Module 4 (`_validate_lemma`, lemma.md §7.5) rejects it. (A
`#@ lemma \trusted` shim — assumed and warned — is unimplemented; see remains-2.md.)

Committed `# pycsl-expected: FAIL` and STAYS failing.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ \trusted reviewer: test
#@ ensures \result >= 0
#@ assigns \nothing
def opaque() -> int:
    return 0


#@ lemma
#@ ensures opaque() >= 0
#@ assigns \nothing
def leaky() -> None:
    x = opaque()
