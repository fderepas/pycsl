r"""Test 1810 — ROUTE #217 CONTROL (expected PASS): `bytearray` is MUTABLE and unaffected.

The route #217 repair types a local bound from the `bytes(...)` constructor as `"bytes"`,
which makes `PYCSL-SEM-SUBSCRIPT` refuse an item store into it. The refusal must be about
IMMUTABILITY, not about byte buffers: the identical program over `bytearray([1, 2, 3])`
must still verify, and CPython agrees (`b[0] = 9` then `b[0]` is 9).

Without this control the repair would be indistinguishable from a ban on byte buffers.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == 9
def f() -> int:
    b = bytearray([1, 2, 3])
    b[0] = 9
    return b[0]
