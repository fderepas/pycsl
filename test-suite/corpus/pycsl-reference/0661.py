"""Test 0661 — Track C (b-p4-rev2 §4(c)): a representation invariant discharges a callee's array
preconditions, collapsing the per-call range obligations.

`_pack_inode` faithfully REQUIRES its 18 field ranges (the real leaves raise out-of-range, so the
ranges are genuine — not narrowable, b-p4-rev2 §3). A caller cannot drop them; but a class whose fields
array carries those bounds as a REPRESENTATION INVARIANT (`0 <= self.fields[k] <= MAX`) discharges all
18 at the call site `_pack_inode(self.fields)` FROM the invariant — no per-call re-derivation. Needs the
field-access-arg passthrough (self.fields must reach the callee, not a placeholder) + L0' (array-field
access in the invariant → Array.get); does NOT need L0" (no function call in the invariant)."""
#@ requires \valid(fields, 18)
#@ requires 0 <= fields[0] and fields[0] <= 4294967295
#@ requires 0 <= fields[1] and fields[1] <= 65535
#@ requires 0 <= fields[2] and fields[2] <= 65535
#@ requires 0 <= fields[3] and fields[3] <= 65535
#@ requires 0 <= fields[4] and fields[4] <= 65535
#@ requires 0 <= fields[5] and fields[5] <= 65535
#@ requires 0 <= fields[6] and fields[6] <= 4294967295
#@ requires 0 <= fields[7] and fields[7] <= 4294967295
#@ requires 0 <= fields[8] and fields[8] <= 4294967295
#@ requires 0 <= fields[9] and fields[9] <= 4294967295
#@ requires 0 <= fields[10] and fields[10] <= 4294967295
#@ requires 0 <= fields[11] and fields[11] <= 4294967295
#@ requires 0 <= fields[12] and fields[12] <= 4294967295
#@ requires 0 <= fields[13] and fields[13] <= 4294967295
#@ requires 0 <= fields[14] and fields[14] <= 4294967295
#@ requires 0 <= fields[15] and fields[15] <= 4294967295
#@ requires 0 <= fields[16] and fields[16] <= 4294967295
#@ requires 0 <= fields[17] and fields[17] <= 4294967295
#@ assigns \nothing
#@ ensures \length(\result) == 64
#@ \trusted reviewer: c-probe
def _pack_inode(fields: list) -> list:
    return bytes(64)

#@ class invariant \length(self.fields) == 18
#@ class invariant 0 <= self.fields[0] and self.fields[0] <= 4294967295
#@ class invariant 0 <= self.fields[1] and self.fields[1] <= 65535
#@ class invariant 0 <= self.fields[2] and self.fields[2] <= 65535
#@ class invariant 0 <= self.fields[3] and self.fields[3] <= 65535
#@ class invariant 0 <= self.fields[4] and self.fields[4] <= 65535
#@ class invariant 0 <= self.fields[5] and self.fields[5] <= 65535
#@ class invariant 0 <= self.fields[6] and self.fields[6] <= 4294967295
#@ class invariant 0 <= self.fields[7] and self.fields[7] <= 4294967295
#@ class invariant 0 <= self.fields[8] and self.fields[8] <= 4294967295
#@ class invariant 0 <= self.fields[9] and self.fields[9] <= 4294967295
#@ class invariant 0 <= self.fields[10] and self.fields[10] <= 4294967295
#@ class invariant 0 <= self.fields[11] and self.fields[11] <= 4294967295
#@ class invariant 0 <= self.fields[12] and self.fields[12] <= 4294967295
#@ class invariant 0 <= self.fields[13] and self.fields[13] <= 4294967295
#@ class invariant 0 <= self.fields[14] and self.fields[14] <= 4294967295
#@ class invariant 0 <= self.fields[15] and self.fields[15] <= 4294967295
#@ class invariant 0 <= self.fields[16] and self.fields[16] <= 4294967295
#@ class invariant 0 <= self.fields[17] and self.fields[17] <= 4294967295
class Inode:
    #@ requires \valid(initial, 18)
    #@ requires 0 <= initial[0] and initial[0] <= 4294967295
    #@ requires 0 <= initial[1] and initial[1] <= 65535
    #@ requires 0 <= initial[2] and initial[2] <= 65535
    #@ requires 0 <= initial[3] and initial[3] <= 65535
    #@ requires 0 <= initial[4] and initial[4] <= 65535
    #@ requires 0 <= initial[5] and initial[5] <= 65535
    #@ requires 0 <= initial[6] and initial[6] <= 4294967295
    #@ requires 0 <= initial[7] and initial[7] <= 4294967295
    #@ requires 0 <= initial[8] and initial[8] <= 4294967295
    #@ requires 0 <= initial[9] and initial[9] <= 4294967295
    #@ requires 0 <= initial[10] and initial[10] <= 4294967295
    #@ requires 0 <= initial[11] and initial[11] <= 4294967295
    #@ requires 0 <= initial[12] and initial[12] <= 4294967295
    #@ requires 0 <= initial[13] and initial[13] <= 4294967295
    #@ requires 0 <= initial[14] and initial[14] <= 4294967295
    #@ requires 0 <= initial[15] and initial[15] <= 4294967295
    #@ requires 0 <= initial[16] and initial[16] <= 4294967295
    #@ requires 0 <= initial[17] and initial[17] <= 4294967295
    #@ assigns self.fields
    def __init__(self, initial: list) -> None:
        self.fields: list = initial

    #@ requires True
    #@ assigns \nothing
    #@ ensures \length(\result) == 64
    def pack(self) -> list:
        # the call: its 18 range preconditions must discharge from the class invariant on self
        return _pack_inode(self.fields)
