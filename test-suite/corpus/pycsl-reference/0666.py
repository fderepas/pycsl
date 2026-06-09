"""Test 0666 — `#@ for VAR in range(lo, hi):` contract-expansion sugar (sugar-for-spec.md).

Bounded macro-expansion: the `#@ for` block desugars (Module3) to ground `requires`/`ensures`, one per
index, with the loop variable substituted by an integer literal — NOT a `\\forall` (so no E-matching
cost). Here a fixed-size 4-byte buffer's range constraints are written once as a loop; they expand to
four ground `requires 0 <= buf[k] and buf[k] <= 255` (k = 0..3, upper-exclusive). The expansion is
byte-identical to the hand-written clauses (the sugar is a spelling, not a meaning), and the function
proves end-to-end. v1: integer-literal range bounds."""
#@ requires \length(buf) >= 4
#@ for k in range(0, 4):
#@     requires 0 <= buf[k] and buf[k] <= 255
#@ ensures \result >= 0 and \result <= 1020
#@ ensures \result == buf[0] + buf[1] + buf[2] + buf[3]
def sum4(buf: list) -> int:
    return buf[0] + buf[1] + buf[2] + buf[3]
