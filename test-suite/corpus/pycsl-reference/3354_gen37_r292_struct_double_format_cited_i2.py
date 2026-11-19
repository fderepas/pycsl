r"""Test 3354 -- route #292 (expected FAIL): census sibling: `<dd` (two float64 slots) also has slot id `i2`; citing `UnixFs.Struct.i2.round_trip` (proved for `>HH`) proved `\result == x0`; CPython rounds through float64: roundtrip(2**53 + 1, 0) is 9007199254740992.0.
Now the law is keyed on the exact format; goal unproven.
"""
# pycsl-expected: FAIL
import struct


#@ ensures \result == x0
#@ proof rocq UnixFs.Struct.i2.round_trip
def roundtrip(x0: int, x1: int) -> int:
    packed = struct.pack("<dd", x0, x1)
    out_x0, _out_x1 = struct.unpack("<dd", packed)
    return out_x0


if __name__ == "__main__":
    assert roundtrip(2 ** 53 + 1, 0) != 2 ** 53 + 1
