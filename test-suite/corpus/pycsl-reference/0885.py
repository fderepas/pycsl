"""Test 0885 — faithful whole-list `str.split(sep)` comprehension → `array string` (POSITIVE).

Exercises the whole-list split lowering (`_split_comp_array_string`): a comprehension
`[<str-elt> for t in <string>.split(sep)]` — a single generator over a string split whose
element expression is itself string-typed once the loop target is bound to a string — is a
faithful `array string` (opaque, `length >= 0`), the whole-list counterpart of the split-ELEM
path `<split>[i]`. Before this, such a comprehension collapsed to the opaque int `list_comp`,
so a `List[str]` return built by `[p.strip() for p in s.split(",")]` failed to type-check
(`int` where `array string` expected).

Faithful under-approximation: content is unmodelled (like `str_split_elem_op`), only the
type + a sound `length >= 0` law matter for the type-safety + frame contract. If this
regresses, the split-shape recognizer, the string-element gate (loop-var typed str), or the
`str_split_op` array-string result broke. Non-@mutable_state path — byte-identical corpus.
"""
from typing import List


#@ requires True
#@ ensures True
#@ assigns \nothing
def split_slots(rt: str) -> List[str]:
    inner = rt.strip()
    if inner.startswith("(") and inner.endswith(")"):
        inner = inner[1:-1]
    return [p.strip() for p in inner.split(",")]
