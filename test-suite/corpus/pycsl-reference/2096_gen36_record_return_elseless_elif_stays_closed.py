r"""Test 2096 — gen #36 (expected FAIL): CONTROL — an `if/elif` chain with no final `else`
(the `orelse` is an else-less `if`, so it does not END in a return) followed by a tail
return. The If lowering would emit `<if-expr>; <rest>` here, so the seam's gate rejects the
shape and the function keeps today's `raise (Return <record>)` (Why3 rejects it:
fail-closed refusal). The claim is true.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


@dataclass
class P:
    x: int
    y: int



#@ ensures \result.x >= 1
#@ assigns \nothing
def k(c: int) -> P:
    if c > 0:
        return P(1, c)
    elif c < 0:
        return P(2, c)
    return P(3, 0)
