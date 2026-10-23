r"""Test 1888 — gen #31 WITNESS (expected FAIL): the `#@ proof` prover keyword is read.

The SIXTH member of the family and the only one that is more than a diagnostic. `rocqq` is
not `rocq` and not `lean`, and the emitted `.mlw` used to be BYTE-IDENTICAL to the correctly
spelled version — the keyword was not dropped, it was NOT READ.

THE BOUND ON THIS ONE WAS WRITTEN WRONG FIRST AND THEN CHECKED, which is why it is worth a
witness rather than a note. `bin/check-proof-crosscheck.sh` walks the DRIVERS' citations and
`proof2why3/crosscheck_ir.py` selects them with

    rocq_qns = sorted({d.qualname for d in directives if d.prover == "rocq"})

so a citation spelled `rocqq` is INVISIBLE TO THE 3-WAY CROSS-CHECK while its axiom is still
emitted into the file's proof. What still bounds it: the axiom BODY comes from
`_AXIOM_REGISTRY`, an unregistered qualname is refused outright, and registry entries are
reviewed source changes — so the reachable outcome is "a typo hides a citation from the
audit", not "arbitrary axioms".

Census: 279 `#@ proof` sites in the tree (147 `rocq`, 132 `lean`), every one correct.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ proof rocqq Pycsl.Reference.Gcd.gcd_0


#@ \abstract
#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result == gcd(a, b)
#@ assigns \nothing
def gcd(a: int, b: int) -> int:
    return 0


#@ requires a >= 0
#@ ensures \result == a
#@ assigns \nothing
def use(a: int) -> int:
    return gcd(a, 0)
