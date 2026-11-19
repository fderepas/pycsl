"""WL-06c FALSE-TWIN (T9) — the byte-RANGE invariant must NOT prove a SPECIFIC byte
VALUE of an unknown param. Verdict: UNPROVEN.

The soundness oracle for WL-06c: the implicit `requires forall i. 0<=b[i]<256` only
adds the RANGE bound; it does NOT pin the content of an unknown `bytes` PARAMETER. So a
claim about the EXACT byte value (`\result == 97`) must stay UNPROVEN — only a user
`requires` can bound the unknown content (see the user-requires driver). If this ever
PROVES, the range model is OVER-CLAIMING (unsound)."""
# pycsl-expected: FAIL
_ = 0


#@ requires 0 <= i and i < len(b)
#@ ensures \result == 97
def claim_specific_UNSOUND(b: bytes, i: int) -> int:
    """FALSE: the range bound does not fix the byte value — must NOT prove."""
    return b[i]
