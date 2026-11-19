r"""Test 3352 -- route #292 (expected FAIL): red-team st001: `struct.pack(">??", x0, x1)` then unpack, citing `UnixFs.Struct.i2.round_trip` (proved for `>HH`), PROVED `\result == x0`; CPython roundtrip(5, 0) is True (1).
Now the law is keyed on the exact format: `>??` gets a format-keyed symbol; goal unproven.
"""
# pycsl-expected: FAIL
import struct


#@ ensures \result == x0
#@ proof rocq UnixFs.Struct.i2.round_trip
def roundtrip(x0: int, x1: int) -> int:
    packed = struct.pack(">??", x0, x1)
    out_x0, _out_x1 = struct.unpack(">??", packed)
    return out_x0


if __name__ == "__main__":
    assert roundtrip(5, 0) != 5
