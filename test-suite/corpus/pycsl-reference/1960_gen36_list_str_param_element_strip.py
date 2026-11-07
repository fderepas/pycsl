r"""Test 1960 — gen #36 (expected PASS): an element read `raw[i]` of a FORMAL `List[str]`
param is classified as a STRING. WL-04 already emits the param as `array string`, so
`raw[i]` lowers to a real `string`; the classifier did not carry the declared element type,
so `raw[i].strip()` fell to an opaque int op applied to a string (L3-tc failure at base).
Now it is `str_strip_op raw[i]`, whose length law (`<=`) proves the claim. Twin: 1961.
"""
# pycsl-expected: PASS
from __future__ import annotations
from typing import List


#@ requires 0 <= i and i < len(raw)
#@ ensures \result <= len(raw[i])
def stripped_len(raw: List[str], i: int) -> int:
    return len(raw[i].strip())
