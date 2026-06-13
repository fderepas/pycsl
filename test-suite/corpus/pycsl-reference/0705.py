"""Test 0705 — #@ sibling_concrete (allocator-frame plan §2.7): opt-in concrete sibling call.

A `self.<m>()` call to a method marked `#@ sibling_concrete` lowers to a CONCRETE call
`(c__bump self)` instead of the default abstract `val` stub, so the caller inherits the
callee's FULL contract AND its class-invariant guarantee on the post-state (the abstract
stub conveys neither). Here `bump` (marked) maintains `#@ class invariant self.x >= 0`;
`bump_loop` calls `self.bump()` inside a loop and carries the invariant as a loop invariant,
re-established each iteration from the concrete callee. The directive is OPT-IN and decoupled
from `no_inline` — without the marker every `self.<m>()` keeps its abstract-stub lowering, so
existing files are byte-identical.

This mirrors the os allocators: `_alloc_block`'s loop calls the `#@ sibling_concrete`
`_set_bitmap` and inherits the disk class invariant as an atom (uniq/inode_bytes_valid).
"""


#@ class invariant self.x >= 0
class C:
    #@ assigns self.x
    #@ ensures self.x == 0
    def __init__(self) -> None:
        self.x: int = 0

    #@ assigns self.x
    #@ ensures self.x == \old(self.x) + 1
    #@ sibling_concrete
    def bump(self) -> None:
        self.x = self.x + 1

    #@ requires n >= 0
    #@ assigns self.x
    def bump_loop(self, n: int) -> None:
        # The class invariant `self.x >= 0` must be re-established after each
        # `self.bump()` — discharged from the CONCRETE callee's contract + its
        # type-invariant guarantee (the sibling_concrete benefit). An abstract stub
        # would not convey the class-invariant guarantee on the post-state.
        #@ loop invariant 0 <= i and i <= n
        #@ loop invariant self.x >= 0
        #@ loop variant n - i
        for i in range(n):
            self.bump()
