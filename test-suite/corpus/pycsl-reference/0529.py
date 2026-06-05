"""Test 0529 — field-referencing method ensures propagate to call site (A2c).

A getter `def get_x(self) -> int: #@ ensures \\result == self.x` is the canonical
*field-referencing* contract: its postcondition relates `\\result` to a self-FIELD,
not to a param or a constant. Before A2c such a clause propagated NOWHERE — both
`_build_method_result_ensures_map` (result-and-constants only) and
`_build_method_param_result_ensures_map` (result-and-params only) explicitly drop
`FieldGet`, so `b.get_x()` lowered to a bare abstract op with no `ensures` and the
driver could prove nothing about the returned value.

A2c adds the third map (`_build_method_field_result_ensures_map`): a clause that
references `\\result` and self-fields only (no params, `\\old`, or locals) DOES
propagate, with the abstract op taking the receiver record as an explicit leading
parameter `(self: <class>)` so `self.x` is bound. The driver constructs `Box(7)`
(so `b.x` is concretely 7) and the propagated `ensures { result = b.x }` then
discharges `\\result == 7`. Companion to 0522 (param-referencing, A2a), which
documented this field case as the remaining gap.
"""
_ = 0  # anchor


class Box:
    def __init__(self, v: int):
        self.x = v

    #@ ensures \result == self.x
    #@ assigns \nothing
    def get_x(self) -> int:
        return self.x


#@ ensures \result == 7
#@ assigns \nothing
def driver() -> int:
    b = Box(7)
    return b.get_x()
