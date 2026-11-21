"""Test 0862 — WL-06c regression lock (POSITIVE): byte-RANGE invariant for an UNKNOWN
`bytes`/`bytearray` PARAMETER.

wrong-lowering-to-fix.md §WL-06c. WL-06b made a `bytes` LITERAL's content faithful, from
which `0 <= b[i] < 256` is DERIVABLE. For an UNKNOWN `bytes` PARAMETER the content is
arbitrary to the solver — but EVERY real Python `bytes`/`bytearray` object has all
elements in [0, 256). PyCSL now emits that byte-range fact as an IMPLICIT precondition
(`requires forall i. 0<=i<len(b) -> 0<=b[i]<256`) for every bytes/bytearray param, so a
byte read of an UNKNOWN param is provably in range WITHOUT the user writing the bound.

Ground truth: the read is a coherent `int` byte cell and — as a type-level guarantee of
the `bytes`/`bytearray` type — is in [0, 256). The EXACT value stays opaque (twin 0863).
Companion to 0836 (the same range invariant for a LITERAL).
"""
_ = 0  # anchor


#@ requires 0 <= i and i < len(b)
#@ ensures 0 <= \result and \result < 256
def byte_in_range(b: bytes, i: int) -> int:
    """An unknown `bytes` param's byte is provably in [0,256) — no user requires."""
    return b[i]


#@ requires 0 <= i and i < len(b)
#@ ensures 0 <= \result and \result < 256
def bytearray_in_range(b: bytearray, i: int) -> int:
    """Same for a `bytearray` param — the invariant covers both byte classes."""
    return b[i]


if __name__ == "__main__":
    assert 0 <= byte_in_range(b"abc", 1) < 256
    assert byte_in_range(b"abc", 1) == ord("b")
    assert 0 <= bytearray_in_range(bytearray(b"xy"), 0) < 256
