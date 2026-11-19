"""Test 0863 — WL-06c regression lock (NEGATIVE twin of 0862). # pycsl-expected: FAIL

Guards the WL-06c byte-range invariant from OVER-CLAIMING. The implicit
`requires forall i. 0<=b[i]<256` adds only the RANGE bound — it does NOT pin the CONTENT
of an unknown `bytes` PARAMETER. So a claim about the SPECIFIC byte value must NOT be
provable; only a user-supplied `requires` can bound the unknown content (see 0864).

Here `claim_specific_UNSOUND` returns `b[i]` but claims `\result == 97` for an arbitrary
`bytes` param. This is FALSE for any byte that isn't `97` (e.g. b"Zb"[0] == 90). If this
test ever PASSES, the range model has collapsed into fixing a concrete byte value
(unsound over-claim).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires 0 <= i and i < len(b)
#@ ensures \result == 97
def claim_specific_UNSOUND(b: bytes, i: int) -> int:
    """Claims the byte is exactly 97 — FALSE for an unknown param; must NOT prove."""
    return b[i]


if __name__ == "__main__":
    # For b = b"Zb", index 0: returns b[0] == 90, but the contract claims == 97. FALSE.
    assert claim_specific_UNSOUND(b"Zb", 0) == ord("Z")
