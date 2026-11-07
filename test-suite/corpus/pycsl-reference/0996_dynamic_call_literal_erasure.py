"""Test 0996 — a call whose CALLEE is not a plain name was erased to the LITERAL 0, and a
literal is a WRONG value rather than an unknown one. ROUTE #24, off
`bin/check-computed-rhs-erasure.py`'s ratchet of 2.

The generic expression fall-through for `<computed>(...)` — `type(self)(...)`,
`self.fns[0]()`, a constructor chosen at runtime — returned `"0"` when no recognizer
claimed the callee. Measured, before the fix, on exactly this body with
`#@ ensures \result == 0`:

    [+] Verification SUCCESS! All contracts formally proven.

while Python returns 7. The emitted body was

    let o = ref 0 in  o := 0;
    if (!o <> 0) then raise (Return 7) else raise (Return 0)

An object is ALWAYS truthy in Python; the literal `0` never is. So the model took the
branch Python cannot take.

NOTE WHICH READ EXPOSED IT, because it is the transferable part. The SAME erasure with a
plain field read — `o = type(self)(); return o.v` under the same false `ensures` — did
NOT prove, because `get_v` is an abstract getter and the result is unconstrained. The
defect was never that the constructed value is lost. It is that the model got to DECIDE A
BRANCH on a value it had invented. Any erasure to a literal is one `if` away from being a
false proof; an erasure to an opaque value is not.

CONTROL: `o = C()` — a real constructor, statically named — always FAILED this contract,
which localises the defect to the fall-through rather than to the contract.

FIXED as an APPLIED program `val opaque_dynamic_call (u: int) : int`. Why3 gives each
APPLICATION a fresh unconstrained result, so nothing about the value proves in either
direction. A `val` CONSTANT would have been wrong for a different reason: two distinct
dynamic calls would then be provably EQUAL. This is what the erasure's own comment had
always claimed it was doing.

NOT A CAPABILITY, deliberately. `type(self)` is the RUNTIME class, which under
inheritance need not be the statically known one, so lowering it to that class's record
constructor would trade a demonstrated unsoundness for a subtler one. The honest fix here
is opacity, and the companion `\result == 7` variant correctly fails too.

CENSUS: exactly ONE site tree-wide — `pure_ast._Unparser.unparse_inner`'s
`type(self)(_avoid_backslashes=True)`, which is precisely what `computed-rhs-erasure` had
been counting — and ZERO in either corpus. The ratchet goes 2 -> 1.

This file is `pycsl-expected: FAIL`: the postcondition is FALSE of the program.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    #@ requires True
    #@ ensures self.v == 7
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 7

    #@ requires True
    #@ ensures \result == 0
    #@ assigns \nothing
    def make(self) -> int:
        o = type(self)()
        if o:
            return 7
        return 0


if __name__ == "__main__":
    print(C().make())
