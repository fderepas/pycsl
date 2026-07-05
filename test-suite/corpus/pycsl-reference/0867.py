"""Test 0867 — WL-06d regression lock (POSITIVE): `bytes([...])` constructor content law
under the ValueError-as-precondition.

wrong-lowering-to-fix.md §WL-06d (P3). `bytes([65,66,67])`/`bytearray([...])` lowers to
`bytes_new`/`bytearray_new`, whose ensures preserve length + per-element content
(`result[i] == x[i]`). WL-06d adds a `requires forall i. 0<=x[i]<256` (Python raises
`ValueError: bytes must be in range(0, 256)` for an out-of-range element). Here every
literal element is in range, so the precondition discharges and the content read PROVES;
the out-of-range twin (0868) fails closed.
"""
_ = 0  # anchor


#@ ensures \result == 65
def ctor_first() -> int:
    b = bytes([65, 66, 67])
    return b[0]


#@ ensures \result == 67
def ctor_last_ba() -> int:
    b = bytearray([65, 66, 67])
    return b[2]


#@ ensures 0 <= \result and \result < 256
def ctor_range() -> int:
    b = bytes([1, 255, 128])
    return b[1]


if __name__ == "__main__":
    assert bytes([65, 66, 67])[0] == 65
    assert bytearray([65, 66, 67])[2] == 67
    assert 0 <= bytes([1, 255, 128])[1] < 256
