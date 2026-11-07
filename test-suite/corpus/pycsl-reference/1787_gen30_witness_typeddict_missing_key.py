r"""Test 1787 — WITNESS: a `total=True` TypedDict literal missing a declared key.

T9 / PEP 589 (typeddict-twoplane-spec.md §1.3). GAP-001: the missing field USED to be
silently filled with its default, bypassing the obligation the TypedDict declares. It is
now a static error. One of the refusals `bin/check-refusal-witness-coverage.py` measured as
having no witness.
"""
# pycsl-expected: FAIL
from typing import TypedDict

_ = 0  # anchor


class Pt(TypedDict):
    x: int
    y: int


#@ assigns \nothing
def build() -> Pt:
    return {"x": 1}
