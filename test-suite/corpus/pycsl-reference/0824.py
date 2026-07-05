"""Test 0824 — WL-06 regression lock (POSITIVE, bytes/bytearray index): a byte
read `b[i]` on a `bytes`/`bytearray` PARAMETER now lowers to a native
`Array.get b i` (a coherent `int` byte read), NOT the opaque
`subscript_get (x:int)(i:int):int`.

Before the fix, a `bytes`/`bytearray` param coarsened to the τ-blessed
`bytes=int†` array-int-backed buffer (`b : array int`, correct), but the subscript
read routed to `val subscript_get (x:int)(i:int):int` applied to `b : array int` —
an `array int` vs `int` type error. Detector D2: TYPEERR, both un-verifiable AND
internally inconsistent. PyCSL now routes a bytes/bytearray subscript read (and
`len(b)`) to the native array backing (`Array.get` / `Array.length`), so `b[i] : int`
type-checks and, under a bounds `requires`, the deterministic read property
`\result == b[i]` is PROVABLE.

Ground truth: the READ is a well-typed, deterministic `int` (the i-th byte cell);
the byte CONTENT stays the τ-blessed opaque residual (a faithful `bytes` value model
is a documented follow-on) — what is soundly provable is that the body read denotes
the SAME cell as the contract read, and that distinct indices are independent cells.
Twin: 0825 (# pycsl-expected: FAIL) asserts a FALSE byte-content claim (a wrong
element / a fixed byte value), which must NOT be provable.
"""
_ = 0  # anchor


#@ requires 0 <= i
#@ requires i < len(b)
#@ ensures \result == b[i]
def read_byte(b: bytes, i: int) -> int:
    """A `bytes` param's byte read is a coherent `int` (was TYPEERR / subscript_get)."""
    return b[i]


#@ requires len(b) >= 2
#@ ensures \result == b[1]
def snd_byte(b: bytearray) -> int:
    """A concrete index reads the SECOND byte cell, independent of the first."""
    return b[1]


if __name__ == "__main__":
    assert read_byte(b"abc", 2) == ord("c")
    assert snd_byte(bytearray(b"xy")) == ord("y")
