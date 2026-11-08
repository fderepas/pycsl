r"""Test 1845 — gen #31 NEGATIVE TWIN of 1844 (expected FAIL): the boundary is the CONTRACT.

Byte-identical to 1844 except that `caller` claims `\result >= 7` — the value `leaf`'s
BODY actually returns — instead of the `\result >= 0` its CONTRACT gives. It must FAIL.

Without this twin, 1844 alone could not distinguish "the cross-group call conveys the
callee's proven contract" from "the cross-group call inlines the callee's body", and the
second would be exactly the axiom-co-residence the directive exists to prevent. The whole
point of `#@ verify_module` is that a group is verified against its neighbours'
INTERFACES; a file that could see through them would make the isolation decorative.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ verify_module LeafMod
    #@ ensures \result >= 0
    #@ assigns \nothing
    def leaf(self) -> int:
        return 7

    #@ verify_module TopMod
    #@ ensures \result >= 7
    #@ assigns \nothing
    def caller(self) -> int:
        return self.leaf()
