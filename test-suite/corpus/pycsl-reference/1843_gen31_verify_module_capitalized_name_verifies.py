r"""Test 1843 — gen #31 CONTROL for 1842 (expected PASS): the capitalized name is fine.

The identical program with `#@ verify_module LeafMod`. It verifies, so the refusal in
1842 is about the NAME SHAPE and not a ban on `#@ verify_module` — the same control
discipline 1841 pays for the `bounded_int` width refusal.

It also pins the boundary the refusal must not cross: `caller` is in the FLAT default
module and `leaf` is in `LeafMod`, so the call crosses the module boundary and is
lowered to the callee's PROVEN contract. `\result >= 0` is exactly what that contract
gives; a claim of `>= 7` (the body's actual value) correctly FAILS, which is how the
boundary is known to convey the contract rather than the body.
"""
# pycsl-expected: PASS
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

    #@ ensures \result >= 0
    #@ assigns \nothing
    def caller(self) -> int:
        return self.leaf()
