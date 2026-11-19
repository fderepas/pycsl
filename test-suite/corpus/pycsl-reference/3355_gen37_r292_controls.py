r"""Test 3355 -- route #292 (expected PASS): CONTROL: the exact `>HH` format `UnixFs.Struct.i2.round_trip` documents still round-trips (in range).
"""
# pycsl-expected: PASS
import struct


#@ requires 0 <= x0 < 65536 and 0 <= x1 < 65536
#@ ensures \result == x0
#@ proof rocq UnixFs.Struct.i2.round_trip
def roundtrip(x0: int, x1: int) -> int:
    packed = struct.pack(">HH", x0, x1)
    out_x0, _out_x1 = struct.unpack(">HH", packed)
    return out_x0


if __name__ == "__main__":
    assert roundtrip(5, 7) == 5
