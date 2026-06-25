"""Test 0349 — `Optional[int]` parameter annotation.

typing-engagement ty1 (25-1700-typing-spec-1): `Optional[X]` reuses the
Union seam — it IS `Union[X, None]`. The annotation synthesizes a per-site
variant `_union_maybe_double_0 = Arm_0_0 int | Arm_0_None`. A function
that takes `Optional[int]` and returns `int` exercises the variant param
path + per-arm VCs (C2 injection, C3 projection). The contract references
only the int return value, not the Union-typed parameter.
"""
from typing import Optional

#@ ensures \result >= 0
#@ assigns \nothing
def maybe_double(x: Optional[int]) -> int:
    return 5

if __name__ == "__main__":
    assert maybe_double(0) == 5
    assert maybe_double(7) == 5
    print("PASS")
