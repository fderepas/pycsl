"""0782 — NEGATIVE: NATIVE size/alignment ('@' prefix) is REJECTED (cleared-pack item 4, UB-7.4b).

# pycsl-expected: FAIL

Native size/alignment (`'@...'`, and Python's default no-prefix) is platform-
dependent: the field sizes AND the inter-field padding depend on the target ABI.
PyCSL cannot soundly model the size law or the round-trip for a native format, so
it REJECTS a `'@'`-prefixed struct format with a clear diagnostic (UB-7.4b) rather
than silently emitting an opaque — but potentially wrongly-sized — model.

This driver uses `struct.pack('@i', x)` and MUST fail at transpilation with the
UB-7.4b native-alignment rejection. Contrast the STANDARD-size `'>i'` (0778),
which has an explicit byte-order prefix and a sound calcsize, and PROVES.
"""
import struct  # noqa


#@ requires -2147483648 <= x and x <= 2147483647
#@ assigns \nothing
#@ ensures \result == x
def roundtrip_native_rejected(x: int) -> int:
    packed = struct.pack('@i', x)
    return struct.unpack('@i', packed)
