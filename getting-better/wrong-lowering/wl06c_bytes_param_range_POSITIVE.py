"""WL-06c POSITIVE (T9) — the implicit byte-RANGE invariant for an UNKNOWN `bytes`
PARAMETER. Verdict: PROVEN.

WL-06b made a `bytes` LITERAL's content faithful, from which `0 <= b[i] < 256` is
DERIVABLE. For an UNKNOWN `bytes`/`bytearray` PARAMETER the content is arbitrary to the
solver — but EVERY real Python `bytes` object has all elements in [0,256). WL-06c emits
that byte-range fact as an IMPLICIT precondition
(`requires forall i. 0<=i<len(b) -> 0<=b[i]<256`) for every bytes/bytearray param, so
`0 <= b[i] < 256` PROVES for an unknown param WITHOUT the user writing the bound. The
range invariant is additive on the τ-blessed coarse `array int` shape and sound (a
false SPECIFIC-value claim stays UNPROVEN — see the false-twin driver)."""
_ = 0


#@ requires 0 <= i and i < len(b)
#@ ensures 0 <= \result and \result < 256
def byte_in_range(b: bytes, i: int) -> int:
    """Range [0,256) provable for an UNKNOWN bytes param — no user requires needed."""
    return b[i]


#@ requires 0 <= i and i < len(b)
#@ ensures 0 <= \result and \result < 256
def bytearray_in_range(b: bytearray, i: int) -> int:
    """Same for a `bytearray` param (the invariant applies to both byte classes)."""
    return b[i]
