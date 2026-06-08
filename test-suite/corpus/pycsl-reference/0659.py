"""Test 0659 — L0′ (challenging-the-plan §4.1): array-FIELD access in a class invariant → Array.get.

A coupling-style class invariant `self._v{n} == self.disk[2n]*256 + self.disk[2n+1]` (the data-refinement
shape: an abstract field coupled to a disk slice). Previously `self.disk[n]` in a class invariant lowered
to an UNBOUND `subscript_get` (the L0 array-indexing gap recurring for fields-in-invariants — the class
invariant emission set `_in_spec`/`_emit_record_ctx` but not `_current_self_type`, so the field's array
type didn't resolve). L0′ sets `_current_self_type` during invariant emission + emits `Array.get` for an
array-field access in spec context. `write0` touches inode 0's slice; the OTHER couplings hold by frame.
"""
#@ class invariant \length(self.disk) == 8
#@ class invariant self._v0 == self.disk[0] * 256 + self.disk[1]
#@ class invariant self._v1 == self.disk[2] * 256 + self.disk[3]
#@ class invariant self._v2 == self.disk[4] * 256 + self.disk[5]
#@ class invariant self._v3 == self.disk[6] * 256 + self.disk[7]
class FS:
    #@ assigns self.disk, self._v0, self._v1, self._v2, self._v3
    #@ ensures self._v0 == 0
    def __init__(self) -> None:
        self.disk: list = [0] * 8
        self._v0: int = 0
        self._v1: int = 0
        self._v2: int = 0
        self._v3: int = 0

    #@ requires 0 <= val and val <= 65535
    #@ assigns self.disk, self._v0
    #@ ensures self._v0 == val
    def write0(self, val: int) -> None:
        self.disk[0] = val // 256
        self.disk[1] = val % 256
        self._v0 = val
