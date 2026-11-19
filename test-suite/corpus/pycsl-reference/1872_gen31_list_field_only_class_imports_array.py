r"""Test 1872 — gen #31: a class whose ONLY array is a FIELD now imports `array.Array`.

Before this, the emitted preamble carried `use int.Int`, `use ref.Ref` and nothing else
while the record declaration said `type c = { mutable xs: array int }` — so the file died
on `unbound type symbol 'array'`, a Why3-internal message naming nothing the user wrote. A
whole shape of program (a class that HOLDS a list and does no other array work) could not
be verified at all.

The `needs_array` disjunction already had the right rule and a comment stating it exactly —
"the record decl is emitted from the FIELD, so the `use` must be pulled from the field, not
only from the bodies" — with one conjunct too many: `value_type == "string"`. Relaunch #16
had a `List[str]` field in hand and repaired that witness rather than the mechanism its own
comment described.

Note what the file also pins: the field path's model of `[]` is a LENGTH-0 array
(`by { xs = (Array.make 0 0) }`), so the TRUE invariant proves. 1873 is the false twin.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ class invariant \length(self.xs) == 0
class C:
    def __init__(self) -> None:
        self.xs: list = []

    #@ ensures \result >= 0
    #@ assigns \nothing
    def n(self) -> int:
        return 0
