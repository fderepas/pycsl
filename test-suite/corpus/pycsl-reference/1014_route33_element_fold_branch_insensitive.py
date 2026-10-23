"""Test 1014 — ROUTE #33 negative witness: an INDEXED READ of a list local was
constant-folded BRANCH-INSENSITIVELY. The contents twin of 1013.

FALSE OF THE PROGRAM: `c == 0`, so `a = [7]` and Python returns 7.

At the parent commit c4233fed this printed `[+] Verification SUCCESS!`, proving
`\result == 9`, because `_known_collection_elements` — like the size map — is
keyed only by the local's name, so the `else` arm's `[9]` supplied the value read
on the `if` path. A wrong LENGTH is a wrong fact about a container; a wrong
ELEMENT is a wrong VALUE flowing into the result.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires c == 0
#@ ensures \result == 9
#@ assigns \nothing
def f(c: int) -> int:
    if c == 0:
        a = [7]
    else:
        a = [9]
    return a[0]
