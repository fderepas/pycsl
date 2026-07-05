"""Test 0825 — WL-06 regression lock (NEGATIVE twin of 0824). # pycsl-expected: FAIL

Guards the WL-06 fix from becoming VACUOUS or OVER-CLAIMING. Routing a bytes/bytearray
subscript to `Array.get` makes the read COHERENT and type-checking, but the byte
CONTENT is the τ-blessed opaque residual (`bytes=int†`) — so a claim about the SPECIFIC
byte value, or a claim conflating distinct byte cells, must NOT be provable.

Here `conflate_UNSOUND` returns `b[0]` but claims `\result == b[1]`; for a `bytes`
buffer the cells at distinct indices are INDEPENDENT `array int` slots, so this is NOT
provable. If this test ever PASSES, either the cells have collapsed back to a single
opaque value (regression) or the coarse model is over-claiming byte content.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires len(b) >= 2
#@ ensures \result == b[1]
def conflate_UNSOUND(b: bytes) -> int:
    """Returns byte 0 but claims byte 1 — false unless the cells are conflated."""
    return b[0]


if __name__ == "__main__":
    # For b = b"xy": returns b[0], but the contract claims == b[1]. FALSE.
    assert conflate_UNSOUND(b"xy") == ord("x")
