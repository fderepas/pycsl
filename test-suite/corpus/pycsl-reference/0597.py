"""Test 0597 — bitwise NOT `~x` on the int model (0442.md C4).

`~x` is the two's-complement identity `-x - 1` (a genuine int operation, not a type-class
leak). Before this fix `~` lowered to the invalid placeholder `(? x)`. RED on the prior commit.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \result == (-x) - 1
#@ assigns \nothing
def bnot(x: int) -> int:
    return ~x
