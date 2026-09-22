r"""Test 1732 — WITNESS: a `#@ lemma` may not carry a frame.

"a lemma is erased" — it exists to state a fact, so writing to anything is a category
error. Sibling of 1731 (returns a value) and 1733 (`\diverges`).
"""
# pycsl-expected: FAIL
from typing import List

_ = 0  # anchor


#@ lemma
#@ assigns a[0]
#@ ensures 2 + 2 == 4
def triv(a: List[int]) -> None:
    a[0] = 1
