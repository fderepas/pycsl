"""Test 1227 — finding-0700 / Gap 2a's NEGATIVE TEST: the empty-string witness must NOT be
provable for a field that is not empty.

Had Gap 2a been built as documented — "the `str` field defaults to the empty-string witness
`{ template = \"\" }`" — this claim would PROVE, while CPython returns "abc". That is a
brand-new severity-1 route of exactly the family routes #85, #86 and #87 close: an erasure to
a DEFINITE value, which the emitter then proves definite facts from.

**THE FIX AND THE DEFECT DIFFER ONLY IN *WHICH* STRING IS SUPPLIED**, which is why this file
exists: no other test in the suite distinguishes "the field's own literal" from "a type-correct
placeholder", and both make 0700 pass.

Rule (l) — negative-test every new gate by removing the thing it should catch — applied to a
COMPLETENESS fix rather than to a guard. The thing to remove here is the faithfulness, and
what remains must still refuse.

This file is `pycsl-expected: FAIL`.
"""
# pycsl-expected: FAIL


class C:
    s: str

    #@ assigns self.s
    def __init__(self) -> None:
        self.s: str = "abc"


#@ requires True
#@ ensures \result == ""
#@ assigns \nothing
def f() -> str:
    c = C()
    return c.s
