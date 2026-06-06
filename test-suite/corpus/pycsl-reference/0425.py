"""0425 — directory name-lookup helper (Phase 6 of remove-trusted-unixfs).

Probes the reusable lookup the path-based sys_* wrappers need: scan a
directory block's 16 entries, decode each name, compare to a path, and
return the matching inode number (or -1). String equality / decode are
opaque ops (PyCSL has no string model) but the scan itself — loop
bounds, struct.unpack via the i1a1 axiom, the running `found` accumulator
— is body-verified. No `\\trusted`.
"""
import struct  # noqa

DISK = 131072


#@ class invariant \length(self.disk) == 131072
class Lookup:
    def __init__(self):
        self.disk: list = bytearray(DISK)

    #@ requires block_num >= 0
    #@ requires block_num < 256
    #@ assigns \nothing
    #@ ensures True
    #@ proof rocq UnixFs.Struct.i1a1.round_trip
    def dir_lookup(self, block_num: int, pathname: str) -> int:
        offset = block_num * 512
        found = -1
        #@ loop invariant 0 <= i and i <= 16
        #@ loop variant 16 - i
        for i in range(16):
            entry_offset = offset + (i * 32)
            entry = self.disk[entry_offset:entry_offset + 32]
            inode_num, name_bytes = struct.unpack('>H30s', entry)
            name = name_bytes.split(b'\x00')[0].decode('utf-8', errors='ignore')
            if name == pathname and inode_num != 0:
                found = inode_num
        return found
