"""Test 0614 — parametric (per-object) HAPPY via `footprint` (07-1143 R3).

`#@ happy inode_conf(n): protects d.disk[512 + n*64 : 512 + (n+1)*64]` parameterises a
per-object region by `n`. A method binds it with `#@ footprint inode_conf(k)`; at each write
`d.disk[i] = v` the meta-pass injects `#@ check (512 + k*64 <= i and i < 512 + (k+1)*64)` — the
write must stay in object `k`'s region (CONTAINMENT). Here `writer` writes exactly
`d.disk[512 + k*64]`, inside its footprint, so it proves. (Composed with an indexed `assigns`
frame, containment yields per-object PRESERVATION — file B untouched when writing file A.)
"""
# pycsl-flags: --memory-model hoare

#@ happy inode_conf(n):
#@     protects d.disk[512 + n * 64 : 512 + (n + 1) * 64]
#@     except formatter

#@ class invariant \length(self.disk) >= 1024
class Disk:
    def __init__(self) -> None:
        self.disk: list = [0] * 1024


d = Disk()


#@ requires 0 <= k and k < 8
#@ footprint inode_conf(k)
#@ assigns d.disk
def writer(k: int, v: int) -> None:
    d.disk[512 + k * 64] = v


#@ assigns d.disk
def formatter() -> None:
    d.disk[0] = 0
