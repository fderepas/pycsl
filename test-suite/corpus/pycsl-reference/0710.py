"""Test 0710 — void-mutator WRITE POSTCONDITION propagates to the no_inline boundary stub.

A mutating method whose `ensures` relates a self-field to a PARAM (`self.x == v`) — self-field +
param, but NO `\result`, NO `\old`, NO quantifier — used to propagate through NONE of the
method-call ensures maps (`field_old` rejects params; `field_param_result` requires `\result`), so
a `#@ no_inline` method's boundary stub `self__setx_<n>` carried only `writes { self.x }` and a
sibling caller could prove nothing about what the call WROTE. The `field_param_post` map closes it.

This is the SAFE half of the heavy-syscall frame work (plan §2.9): a NON-QUANTIFIED equality
carries no trigger, so it cannot E-match-poison sibling goals (unlike a `\forall k. … == \old`
frame). It is what gives the os `_write_entry`/`_zero_entry` callers their write witness
(`slot_inode(self.disk, b, s) == inode` / `== 0`), taking sys_unlink 3→1 and sys_rmdir 2→1.
"""


class Box:
    #@ assigns self.x
    #@ ensures self.x == 0
    def __init__(self) -> None:
        self.x: int = 0

    #@ no_inline
    #@ assigns self.x
    #@ ensures self.x == v
    def setx(self, v: int) -> None:
        self.x = v

    #@ assigns self.x
    #@ ensures self.x == 7
    def set_seven(self) -> None:
        self.setx(7)
        #@ assert self.x == 7
