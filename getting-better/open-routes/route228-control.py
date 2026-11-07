"""stable_hash COLLISION witness: two struct formats, one emitted term."""
import struct  # noqa


#@ requires True
#@ ensures \result == 1
def go() -> int:
    a = struct.pack('<bb6x', 1, 2)
    b = struct.pack('<hL', 1, 2)
    if len(a) == len(b):
        return 1
    return 0
