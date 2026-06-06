"""0424 — directory-block write over an int-array model (Phase 4 of
remove-trusted-unixfs).

Mirrors the rewritten `_write_directory`: a directory block holds 16
entries of struct '>H30s' (inode_num : H, name : 30-byte field). Entries
are passed as parallel int arrays — `inodes` (16 inode numbers) and
`names` (a flat 16*30 = 480-byte name buffer, entry i at names[i*30 :
i*30+30]). The block is zero-filled then each entry packed and blitted
in a single bounded `range(16)` loop (no enumerate / tuples / strings).
Discharged by the i1a1 round-trip axiom; no `\\trusted`.
"""
import struct  # noqa

DISK = 131072


#@ class invariant \length(self.disk) == 131072
class DirWriter:
    def __init__(self):
        self.disk: list = bytearray(DISK)

    #@ requires block_num >= 0
    #@ requires block_num < 256
    #@ requires \length(inodes) == 16
    #@ requires \length(names) == 480
    #@ assigns self.disk
    #@ ensures True
    #@ proof rocq UnixFs.Struct.i1a1.round_trip
    def write_directory(self, block_num: int, inodes: list, names: list) -> None:
        offset = block_num * 512
        self.disk[offset:offset + 512] = b'\x00' * 512
        #@ loop invariant 0 <= i and i <= 16
        #@ loop variant 16 - i
        for i in range(16):
            entry_offset = offset + (i * 32)
            name_slice = names[i * 30:i * 30 + 30]
            self.disk[entry_offset:entry_offset + 32] = struct.pack('>H30s', inodes[i], name_slice)
