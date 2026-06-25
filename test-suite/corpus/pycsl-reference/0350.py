"""Test 0350 — `Union[int, None]` parameter annotation.

typing-engagement ty1 (25-1700-typing-spec-1): `Union[X, None]` is
`Optional[X]` (C1b). The annotation synthesizes a per-site variant
`_union_maybe_succ_0 = Arm_0_0 int | Arm_0_None`. A function returning
`int` declares `-> int` so the `ensures \result >= 1` contract references
the int return value directly (the Union is on the parameter, exercising
the variant param path + per-arm VCs without a variant-return contract
mismatch).
"""
from typing import Union

#@ requires True
#@ ensures \result >= 1
#@ assigns \nothing
def maybe_succ(x: Union[int, None]) -> int:
    return 1

if __name__ == "__main__":
    assert maybe_succ(1) == 1
    assert maybe_succ(10) == 1
    print("PASS")
