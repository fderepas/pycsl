"""0423 — inode read/write over an 18-int array model (Phase 3 of
remove-trusted-unixfs).

Mirrors the rewritten `_read_inode` / `_write_inode`: an inode is an
18-element `array int` (struct '>IHHHHHII10Ixx' field order), read by
tuple-unpacking a `struct.unpack` result into named locals and building
the array single-exit, written by packing 18 explicit positional args
(no `*spread`) and blitting into the disk field. Discharged by the i18
round-trip axiom; no `\\trusted`.
"""
import struct  # noqa

DISK = 131072


#@ class invariant \length(self.disk) == 131072
class Inodes:
    def __init__(self):
        self.disk: list = bytearray(DISK)

    #@ requires 0 <= inode_num and inode_num < 32
    #@ assigns \nothing
    #@ ensures True
    #@ proof rocq UnixFs.Struct.i18.round_trip
    def read_inode(self, inode_num: int) -> list:
        offset = 512 + (inode_num * 64)
        chunk = self.disk[offset:offset + 64]
        (f0, f1, f2, f3, f4, f5, f6, f7, f8, f9,
         f10, f11, f12, f13, f14, f15, f16, f17) = struct.unpack('>IHHHHHII10Ixx', chunk)
        inode = [f0, f1, f2, f3, f4, f5, f6, f7, f8, f9,
                 f10, f11, f12, f13, f14, f15, f16, f17]
        return inode

    #@ requires 0 <= inode_num and inode_num < 32
    #@ requires \length(inode) == 18
    #@ assigns self.disk
    #@ ensures True
    #@ proof rocq UnixFs.Struct.i18.round_trip
    def write_inode(self, inode_num: int, inode: list) -> None:
        offset = 512 + (inode_num * 64)
        packed = struct.pack('>IHHHHHII10Ixx',
                             inode[0], inode[1], inode[2], inode[3], inode[4],
                             inode[5], inode[6], inode[7], inode[8], inode[9],
                             inode[10], inode[11], inode[12], inode[13], inode[14],
                             inode[15], inode[16], inode[17])
        self.disk[offset:offset + 64] = packed
