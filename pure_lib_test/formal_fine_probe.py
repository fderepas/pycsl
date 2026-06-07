# Fine probe — intra-subsystem framing (making-it-pure-5.md §9)
#
# Tests: After a filesystem mutation (sys_creat on file A), can we
# prove that a different file B's metadata is preserved?
#
# This is the Tier-2 question. With Tier-1 HAPPY, we proved
# cross-subsystem preservation. Here we test intra-subsystem:
# both A and B are fs objects; sys_creat legitimately writes fs.
#
# Expected outcome: this CANNOT be proven with current PyCSL because:
# 1. sys_creat's assigns clause is `self.disk` (the whole disk)
# 2. There's no way to say "only writes inode A, not inode B"
# 3. This is exactly the parametric HAPPY / narrow assigns gap (§10)
#
# We still run this test to document the gap formally.

from pure_lib.os.UnixInodeFileSystem import UnixInodeFileSystem


# --- Fine probe: sys_creat returns valid fd or -1 ---
# This tests that the filesystem stub's contract is usable.
#@ ensures \result == -1 or \result >= 3
def fine_creat_returns_fd() -> int:
    fs = UnixInodeFileSystem()
    fd = fs.sys_creat("test.txt", 0o644)
    return fd
