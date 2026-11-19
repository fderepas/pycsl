"""WL-06d POSITIVE (T10, P3) — `bytes([...])`/`bytearray([...])` constructor content law
under the ValueError-as-precondition. Verdict: PROVEN.

The constructor lowers to `bytes_new`/`bytearray_new` with length+content ensures
(`result[i]==x[i]`) AND a WL-06d range precondition `requires 0<=x[i]<256` (Python raises
`ValueError` for an out-of-range element). Every literal element here is in range, so the
precondition discharges and the content read PROVES."""
_ = 0


#@ ensures \result == 65
def ctor_first() -> int:
    b = bytes([65, 66, 67])
    return b[0]


#@ ensures \result == 67
def ctor_last_ba() -> int:
    b = bytearray([65, 66, 67])
    return b[2]
