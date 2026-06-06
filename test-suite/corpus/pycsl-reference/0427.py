"""0427 — \\array_eq round-trip: write data into a block, read it back, prove
the read-back array equals what was written (extensional content equality).

`self.disk[a:b] = data` lowers to `Array.blit` (dst[a+i] = data[i]); the
read-back `self.disk[a:b]` lowers to `Array.sub` (result[i] = disk[a+i],
length = b-a). Hence `\array_eq(\result, data)` (same length + per-index
equality) closes in pure Why3 — no \trusted, no proof citation. This is the
model-level analog of "write a string then read it back unchanged".
"""

DISK = 131072


#@ class invariant \length(self.disk) >= 131072
class Echo:
    def __init__(self):
        self.disk: list = bytearray(DISK)

    #@ requires block >= 6 and block < 256
    #@ requires \length(data) <= 512
    #@ assigns self.disk
    #@ ensures \array_eq(\result, data)
    def echo(self, block: int, data: list) -> list:
        n = len(data)
        start = block * 512
        self.disk[start:start + n] = data       # Array.blit data 0 disk start n
        return self.disk[start:start + n]        # Array.sub disk start n
