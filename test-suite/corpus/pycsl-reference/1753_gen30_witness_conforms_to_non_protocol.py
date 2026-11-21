r"""Test 1753 — WITNESS: `#@ conforms_to` naming a class that is not a Protocol.

Conformance targets must be `class P(Protocol)` declarations in the same module; naming an
ordinary class would make the declaration look like a checked obligation while checking
nothing. One of the refusals `bin/check-refusal-witness-coverage.py` measured as having no
file proving it can fire. Sibling: 1754 (a class missing a protocol member).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


class NotAProtocol:
    pass


#@ conforms_to NotAProtocol
class C:
    #@ ensures \result == 0
    def m(self) -> int:
        return 0
