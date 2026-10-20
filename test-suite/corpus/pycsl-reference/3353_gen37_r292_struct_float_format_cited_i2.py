r"""Test 3353 -- route #292 (expected FAIL): census sibling: `<ff` shares slot id `i2`; citing `UnixFs.Struct.i2.round_trip` proved `\result == x0`; CPython rounds through float32: roundtrip(16777217, 0) is 16777216.0.
Now unproven.
"""
# pycsl-expected: FAIL
import struct


#@ ensures \result == x0
#@ proof rocq UnixFs.Struct.i2.round_trip
def roundtrip(x0: int, x1: int) -> int:
    packed = struct.pack("<ff", x0, x1)
    out_x0, _out_x1 = struct.unpack("<ff", packed)
    return out_x0


if __name__ == "__main__":
    assert roundtrip(16777217, 0) != 16777217
