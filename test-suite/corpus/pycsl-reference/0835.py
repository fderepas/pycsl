"""Test 0835 — WL-06b regression lock (POSITIVE): FAITHFUL bytes-literal byte CONTENT.

wrong-lowering-to-fix.md §WL-06 (byte-content residual → IMPLEMENTED core). WL-06 made a
`bytes`/`bytearray` subscript READ COHERENT (native `Array.get`); WL-06b makes the byte
CONTENT of a `bytes` LITERAL FAITHFUL. A `bytes` literal `b"abc"` lowers (Module5
`_py_expr_constant`) to an `array int` constructed with the REAL byte values
(`Array.make 3 97; _[1] <- 98; _[2] <- 99`), so a content read denotes the ACTUAL byte:
`b[0] == 97`, `b[1] == 98`, `b[2] == 99` PROVE (ordinals of 'a','b','c'). Hex escapes
carry their real byte too (`b"\\x01\\xff\\x80"` → `[1, 255, 128]`). The coarse
`bytes = int†` `array int` SHAPE is KEPT — this is content faithfulness ON TOP of it,
additive. Twin 0837 (# pycsl-expected: FAIL) asserts a FALSE byte value, which must NOT
prove; 0836 covers the byte-range invariant.
"""
_ = 0  # anchor


#@ ensures \result == 97
def byte0_ascii() -> int:
    """b"abc"[0] is the ordinal of 'a' = 97 (was an opaque residual, now faithful)."""
    b = b"abc"
    return b[0]


#@ ensures \result == 98
def byte1_ascii() -> int:
    """b"abc"[1] = ord('b') = 98 — a distinct, independently-provable cell."""
    b = b"abc"
    return b[1]


#@ ensures \result == 255
def byte_hex() -> int:
    """b"\\x01\\xff\\x80"[1] = 0xff = 255 — hex escapes carry their real byte value."""
    b = b"\x01\xff\x80"
    return b[1]


if __name__ == "__main__":
    assert byte0_ascii() == ord("a")
    assert byte1_ascii() == ord("b")
    assert byte_hex() == 0xFF
