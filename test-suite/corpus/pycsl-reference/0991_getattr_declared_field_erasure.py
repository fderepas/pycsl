"""Test 0991 — `getattr(obj, "field")` on a DECLARED field is no longer erased to the
default. This is ROUTE #22, and it came off `bin/check-computed-rhs-erasure.py`'s
green ratchet of 2.

`expressions._lower_getattr` resolves `getattr(obj, name[, default])` against the record
model and, when the earlier branches miss, EMITS THE DEFAULT. Its comment carried the
soundness argument:

    "the dynamic-config case getattr(self, "_x", {}) where `_x` isn't a declared field
     -> emit the default argument directly. getattr DOES return default for an absent
     attribute, so this is sound; the actual runtime value is opaque to the prover
     (fails-safe: any contract depending on the real value fails to prove, never
     proves false)."

That licence holds only while the attribute really IS absent, and nothing checked.
Measured, before the fix — this exact file, with `#@ ensures \result == 0`:

    [+] Verification SUCCESS! All contracts formally proven.

while Python returns 7. The class emits `type c = { mutable a: int }`, so `a` IS a
declared field; the body lowered to

    let v = ref 0 in  v := 0

— the attribute read is GONE, replaced by the literal default, and the `if` that consumes
it is decided by a constant. So the default is a WRONG value, not an unknown one, which is
precisely what #33 had already recorded about `_refine_tuple_return_type` ("folded to the
LITERAL 0 ... a WRONG value, not an unknown one") without generalising it.

THE 2-ARG FORM WAS WORSE and also proved: `getattr(self, "a")` has no default at all, and
`if len(args_ir) <= 2: return "0"` fabricated a zero out of nothing.

CONTROL: the identical file with `v = self.a` always FAILED, which localises the defect to
the `getattr` lowering rather than to the contract.

THE FIX IS THE COMMENT'S OWN LICENCE TURNED INTO A MACHINE CHECK: a field the emitted
record DECLARES is present, so `getattr(o, "f", d)` IS `o.f` and lowers as the real read.
`_emitted_record_field_labels` is the per-class oracle. (The pre-existing
`_all_record_fields` branch is a UNION over every class AND is gated on `@mutable_state`,
which is exactly why the corpus was outside it.) ABSENCE still takes the default: a name
the record does not declare is genuinely missing at runtime too.

So this is a CAPABILITY, not a refusal — the companion `0992` proves the TRUE
postcondition `\result == 7` on the same body, which nothing could do before.

CENSUS: 28 fall-through sites in the mirror, 1 in the corpus. 20 are `self.<runtime cache>`
reads of names the record does not declare (faithful, but by luck); 5 are objects of
unknown static type; 2 read a field the model DECLARES — `Module5_IREmitter` `node.index`
on `CtorPayload`, and `stmt_control_flow` `getattr(stmt, "finalbody", None)` on `TryStmt`,
which had made ROUTE #21'S OWN REFUSAL dead code in the mirror's model. The corpus's one
real site (`python-reference/0078`) has a NON-literal name and is untouched.

This file is `pycsl-expected: FAIL`: the postcondition is FALSE of the program, so failing
to prove it IS the correct verdict.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    #@ requires True
    #@ ensures self.a == 7
    #@ assigns self.a
    def __init__(self) -> None:
        self.a: int = 7

    #@ requires self.a == 7
    #@ ensures \result == 0
    #@ assigns \nothing
    def get(self) -> int:
        v = getattr(self, "a", 0)
        if v:
            return 7
        return 0


if __name__ == "__main__":
    print(C().get())
