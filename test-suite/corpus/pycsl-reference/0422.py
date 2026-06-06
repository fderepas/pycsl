"""0422 — array-slice assignment with an array RHS (Phase 2 of
remove-trusted-unixfs).

Validates Module6 lowering of `self.disk[a:b] = <array int>` (a
`struct.pack` result or a `b'\\x00' * N` zero-fill) into a bounded
array blit into a record-array field. This is documented gap 4 of
missing-pycsl-ir-features.md, and the only real compiler change the
de-trust rewrite needs (everything else is sidestepped in Python).
"""
import struct  # noqa

DISK = 4096


#@ class invariant \length(self.disk) == 4096
class Blitter:
    def __init__(self):
        self.disk: list = bytearray(DISK)

    #@ requires 0 <= off and off + 64 <= 4096
    #@ assigns self.disk
    #@ ensures True
    #@ proof rocq UnixFs.Struct.i18.round_trip
    def write_block(self, off: int, a: int, b: int) -> None:
        packed = struct.pack('>IHHHHHII10Ixx', a, b, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.disk[off:off + 64] = packed

    #@ requires 0 <= off and off + 512 <= 4096
    #@ assigns self.disk
    #@ ensures True
    def zero_block(self, off: int) -> None:
        self.disk[off:off + 512] = b'\x00' * 512
