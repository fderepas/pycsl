"""Test 0836 — WL-06b regression lock (POSITIVE): bytes-literal byte-RANGE invariant.

wrong-lowering-to-fix.md §WL-06 (byte-content core). Because a `bytes` LITERAL lowers to
an `array int` built from the REAL byte values (each literally a Python byte, so in
[0, 256)), the byte-RANGE invariant `0 <= b[i] < 256` is DERIVABLE for every index of a
literal — no axiom, it follows from the concrete construction. This locks that a byte
read of a `bytes` literal is provably in range: `read_in_range` reads `b[i]` for an
in-bounds `i` and its contract `0 <= \\result < 256` PROVES. Companion to 0835 (exact
content); guards against a regression that would lose the concrete literal values (and
thus the range).
"""
_ = 0  # anchor


#@ requires 0 <= i
#@ requires i < 3
#@ ensures 0 <= \result
#@ ensures \result < 256
def read_in_range(i: int) -> int:
    """Any byte of the literal b"\\x01\\xff\\x80" = [1,255,128] is in [0,256)."""
    b = b"\x01\xff\x80"
    return b[i]


#@ ensures 0 <= \result
#@ ensures \result < 256
def max_byte() -> int:
    """The largest byte 0xff = 255 is in range — the upper edge holds."""
    b = b"\x00\xff"
    return b[1]


if __name__ == "__main__":
    assert 0 <= read_in_range(0) < 256
    assert 0 <= read_in_range(2) < 256
    assert max_byte() == 255
