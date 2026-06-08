"""C2 micro-probe (c-impl §3 C2): does the field-range representation invariant survive a COMPUTED
mutation (inode[0]=new_size, bounded by disk size) and still discharge the 18 requires?"""
#@ requires \valid(inode, 18)
#@ requires 0 <= inode[0] and inode[0] <= 4294967295
#@ requires 0 <= inode[1] and inode[1] <= 65535
#@ requires 0 <= inode[2] and inode[2] <= 65535
#@ requires 0 <= inode[3] and inode[3] <= 65535
#@ requires 0 <= inode[4] and inode[4] <= 65535
#@ requires 0 <= inode[5] and inode[5] <= 65535
#@ requires 0 <= inode[6] and inode[6] <= 4294967295
#@ requires 0 <= inode[7] and inode[7] <= 4294967295
#@ requires 0 <= inode[8] and inode[8] <= 4294967295
#@ requires 0 <= inode[9] and inode[9] <= 4294967295
#@ requires 0 <= inode[10] and inode[10] <= 4294967295
#@ requires 0 <= inode[11] and inode[11] <= 4294967295
#@ requires 0 <= inode[12] and inode[12] <= 4294967295
#@ requires 0 <= inode[13] and inode[13] <= 4294967295
#@ requires 0 <= inode[14] and inode[14] <= 4294967295
#@ requires 0 <= inode[15] and inode[15] <= 4294967295
#@ requires 0 <= inode[16] and inode[16] <= 4294967295
#@ requires 0 <= inode[17] and inode[17] <= 4294967295
#@ assigns \nothing
#@ \trusted reviewer: c2-probe
def _write_packed(inode: list) -> None:
    return

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

    #@ requires 0 <= new_size and new_size <= 131072
    #@ requires 0 <= tick and tick <= 4294967295
    #@ assigns self.fields
    #@ ensures True
    def update_and_write(self, new_size: int, tick: int) -> None:
        self.fields[0] = new_size      # computed (size), bounded by disk size 131072 < 2^32
        self.fields[7] = tick          # computed (clock tick), bounded
        _write_packed(self.fields)     # 18 requires must discharge AFTER the mutations
