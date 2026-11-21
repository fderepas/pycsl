"""Test 0838 — WL-06b regression lock (NEGATIVE, immutability): a bytes element write is REJECTED. # pycsl-expected: FAIL

wrong-lowering-to-fix.md §WL-06 (byte-content core, immutability). A Python `bytes`
object is IMMUTABLE: `b[i] = v` raises `TypeError: 'bytes' object does not support item
assignment`. PyCSL must therefore REJECT a subscript-store to a `bytes` variable rather
than lower it to an unsound mutable `Array.set` (which would let a caller "prove" a
mutation Python never performs). `write_byte_UNSOUND` binds a `bytes` literal and writes
`b[0] = 5`; the pipeline REJECTS it (PYCSL-SEM-SUBSCRIPT, unconditional — not gated on
annotation), producing a non-SUCCESS result (XFAIL here). If this ever produced a
`Verification SUCCESS`, the immutable-bytes write was silently accepted — an UNSOUND
regression. A mutable byte buffer must be a `bytearray` (or a `list`), whose element
write is a genuine, sound array mutation.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 5
def write_byte_UNSOUND() -> int:
    """A `bytes` element write is a Python TypeError — must be REJECTED, not lowered."""
    b = b"abc"
    b[0] = 5  # TypeError: 'bytes' object does not support item assignment
    return b[0]
