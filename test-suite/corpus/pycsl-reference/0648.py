"""Test 0648 — str class field lowers to a faithful Why3 string (07-2333-rev2 TP-3 / Gap 6).

A `str`-annotated field was collapsed to `int` in the WhyML record (`_name: int`), so any method
comparing/returning it hit `int` vs `string`. The field now lowers to `string` (Module5
_field_type_from_annotation + the record emitter), so a method returning the field proves a
relational postcondition. Class counterpart of the TP-1 str local / str param lowering.
"""
# pycsl-flags: --memory-model hoare


class Box:
    def __init__(self) -> None:
        self._s: str = "x"

    #@ ensures \result == self._s
    #@ assigns \nothing
    def get(self) -> str:
        return self._s
