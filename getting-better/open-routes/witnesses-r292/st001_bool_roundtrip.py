import struct

#@ ensures \result == x0
#@ proof rocq UnixFs.Struct.i2.round_trip
def roundtrip(x0: int, x1: int) -> int:
    packed = struct.pack(">??", x0, x1)
    out_x0, _out_x1 = struct.unpack(">??", packed)
    return out_x0

if __name__ == "__main__":
    assert roundtrip(5, 0) == 5, roundtrip(5, 0)
