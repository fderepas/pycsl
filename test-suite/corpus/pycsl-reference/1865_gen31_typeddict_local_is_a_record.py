r"""Test 1865 — gen #31: a TypedDict LOCAL is constructed AND read as a record.

annotations.md §12.12 promises, with no position excepted, that "construction
`{"x": 1, "y": 2}` becomes a record literal" and "field access `p["x"]` becomes
record-field access `p.x`". Measured in three positions before the repair:

    RETURN     def build() -> Pt: return {"x": 1, "y": 2}     SUCCESS
    PARAMETER  def getx(p: Pt) -> int: return p["x"]          SUCCESS
    LOCAL      p: Pt = {"x": 1, "y": 2}; return p["x"]        FAILED

and the local case's emission showed both halves of ONE variable disagreeing about its
type — the construction taking the generic body-dict path (`map_update_some` over
`map int (option int)`) while the READ took the record projection (`!p.x`):

    type pt = { mutable x: int; mutable y: int }          (* the record IS declared *)
    let p = ref (map_update_some (map_update_some (const (None: option int)) "x" 1) "y" 2) in
    !p.x

Why3 rejects the mismatch, so it was FAIL-CLOSED and not a route — but what a user
following §12.12 got was an error naming two types neither of which they wrote, and no
diagnostic pointing at a position rule that is written down nowhere.

THE CAUSE WAS ONE CONTEXT TEST. `_typeddict_record_literal` detects the construction
context from `_func_return_type` alone — its own docstring says so — while the READ side
looks the receiver up in `_record_types`. Two different context tests on the two halves.

Repaired on the `\trusted`-mirrored side of both seams, which is what kept it cheap:
`_handle_assign_stmt` supplies the construction context from the TARGET's declared type,
and `_emit_first_assign` stops the dict path overwriting the record literal it produces.
The un-trusted `_typeddict_record_literal` and `_first_assign_kind` are untouched.

False twin: 1866, the same file claiming `\result == 4`.
"""
# pycsl-expected: PASS
from typing import TypedDict

_ = 0  # anchor


class Pt(TypedDict):
    x: int
    y: int


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    p: Pt = {"x": 1, "y": 2}
    return p["x"] + p["y"]
