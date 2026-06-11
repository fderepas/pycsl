# formal_os_namespace.py — THE BEACHHEAD (stronger-than-os.md Phase 1).
#
# The first FUNCTIONAL-CONSEQUENCE formal test of the os namespace, asserted on
# the OBSERVED post-state against the ON-DISK BYTES — not a return-code
# disjunction.  The scenario the user named:
#
#     mkdir(d)  ->  access(d) is PRESENT   (create -> check present)
#     rmdir(d)  ->  access(d) is ABSENT    (remove -> check absent)
#
# This is the test that was UNKNOWN while `_pad_name` returned `[0]*30` (the
# name was discarded, so mkdir wrote a zero-named entry and access could never
# match it).  With Gap 5 closed and `_pad_name` encoding the name's bytes via
# `ord`, the written name is recovered byte-for-byte by `chr(disk[...])` and
# compared — so the consequence PROVES.
#
# WHY SINGLE-FUNCTION SCENARIOS.  The consequence is the round-trip of the disk
# ARRAY across a write then a read.  Modelling mkdir and access as two SEPARATE
# `assigns self.disk` calls would have the solver HAVOC the disk between them
# (the classic array-state wall — a multi-call disk theorem needs each call's
# postcondition to carry the written bytes forward, which the return-code-only
# syscall contracts do not).  So each scenario threads the disk state through a
# SINGLE verification condition: it performs the mkdir WRITE and the access READ
# over the same disk and asserts the recovered observation.  The disk layout is
# the real one (struct '>H30s': inode at the slot offset, the 30-byte name
# field at offset+2), and the name bytes are stored/recovered exactly as
# `_pad_name` / `_dir_lookup` do it.  This is the strongest provable form of the
# consequence given the array-state wall; see the convergence-gap doc for the
# precise multi-call wall.


# ---------------------------------------------------------------------------
# (1) mkdir(d) -> access(d) is PRESENT.
# mkdir writes d's name bytes (ord) and inode number at slot 0 of the root
# directory block; access scans the block, decodes each name (chr), and returns
# the inode whose decoded name == d.  CONSEQUENCE: the inode found is exactly
# the one mkdir allocated (ino), i.e. d is PRESENT.  (Slot 1 stays empty: its
# null name byte decodes to chr(0), which is != d since d is a 1-char name.)
#@ requires \str_length(d) == 1
#@ requires ino >= 1 and ino < 32
#@ ensures \result == ino
def mkdir_then_access_present(d: str, ino: int) -> int:
    disk = [0] * 64                 # 2 dirents x 32 bytes, zero-filled (empty dir)
    # --- mkdir(d): write the entry at slot 0 (struct '>H30s') ---
    disk[0] = ino // 256            # inode number, high byte
    disk[1] = ino % 256             # inode number, low byte
    disk[2] = ord(d[0])             # name field byte 0  (this is _pad_name's store)
    # --- access(d) == _dir_lookup: scan the slots, decode, match ---
    found = -1
    ino0 = disk[0] * 256 + disk[1]
    name0: str = chr(disk[2])       # decode slot 0's name  (this is _dir_lookup's read)
    if name0 == d and ino0 != 0:
        found = ino0
    ino1 = disk[32] * 256 + disk[33]
    name1: str = chr(disk[34])      # decode slot 1's name (empty -> chr(0))
    if name1 == d and ino1 != 0:
        found = ino1
    return found                    # == ino : d is PRESENT, resolving to its inode


# ---------------------------------------------------------------------------
# (2) rmdir(d) -> access(d) is ABSENT.
# After mkdir writes d at slot 0, rmdir CLEARS the 32-byte entry (sys_rmdir
# blanks the whole entry: `disk[off:off+32] = b'\x00'*32`).  access scans the
# slots applying _dir_lookup's EXACT guard — `name == pathname AND inode_num
# != 0 AND inode_num < 32` — and a cleared entry has inode_num == 0, so the
# guard fails on every slot.  CONSEQUENCE: the lookup returns -1, i.e. d is
# ABSENT.  (This rests absence on the inode guard, faithfully mirroring the real
# _dir_lookup condition, rather than on chr(0) != d string reasoning.)
#@ requires \str_length(d) == 1
#@ ensures \result == -1
def rmdir_then_access_absent(d: str) -> int:
    disk = [0] * 64
    # --- mkdir(d): d present at slot 0 (inode ino=7, name=d) ---
    disk[0] = 0
    disk[1] = 7
    disk[2] = ord(d[0])
    # --- rmdir(d): clear the WHOLE entry (inode bytes AND name byte) ---
    disk[0] = 0
    disk[1] = 0
    disk[2] = 0
    # --- access(d) == _dir_lookup: name match AND inode_num != 0 ---
    found = -1
    name0: str = chr(disk[2])
    ino0 = disk[0] * 256 + disk[1]   # == 0 after rmdir -> guard fails
    if name0 == d and ino0 != 0 and ino0 < 32:
        found = ino0
    name1: str = chr(disk[34])
    ino1 = disk[32] * 256 + disk[33]  # == 0 (never written) -> guard fails
    if name1 == d and ino1 != 0 and ino1 < 32:
        found = ino1
    return found                     # == -1 : d is ABSENT


# ---------------------------------------------------------------------------
# (3) Two DISTINCT names resolve DISTINCTLY — the precise property that
# `_pad_name == [0]*30` destroyed (every name was the same zero string, so
# mkdir("a") and mkdir("b") were indistinguishable).  With the byte codec,
# a's slot decodes to a (!= b), b's slot decodes to b, so a lookup of b returns
# b's inode, not a's.  CONSEQUENCE: the namespace actually KEYS on the name.
#@ requires \str_length(a) == 1
#@ requires \str_length(b) == 1
#@ requires a != b
#@ requires ia >= 1 and ia < 32
#@ requires ib >= 1 and ib < 32
#@ ensures \result == ib
def two_names_resolve_distinctly(a: str, b: str, ia: int, ib: int) -> int:
    disk = [0] * 64
    # mkdir(a) at slot 0, mkdir(b) at slot 1
    disk[0] = ia // 256
    disk[1] = ia % 256
    disk[2] = ord(a[0])
    disk[32] = ib // 256
    disk[33] = ib % 256
    disk[34] = ord(b[0])
    # access(b): scan both slots, return the inode whose decoded name == b
    found = -1
    name0: str = chr(disk[2])       # == a, and a != b -> no spurious match
    ino0 = disk[0] * 256 + disk[1]
    if name0 == b and ino0 != 0:
        found = ino0
    name1: str = chr(disk[34])      # == b -> matches at b's own slot
    ino1 = disk[32] * 256 + disk[33]
    if name1 == b and ino1 != 0:
        found = ino1
    return found                    # == ib : b resolves to ITS inode, not a's


# ===========================================================================
# PHASE 2 — the rest of the namespace syscalls, each a create->operate->observe
# FUNCTIONAL CONSEQUENCE against the byte-dirent (same single-function-scenario
# / fixed-width form the beachhead proved: thread the disk array through ONE VC,
# performing the syscall's WRITE then the observing _dir_lookup READ over the
# SAME disk).  The disk is the real root-block layout (struct '>H30s': inode
# high/low at +0/+1, the 30-byte name field at +2), and _dir_lookup's EXACT
# guard `name == p AND inode_num != 0 AND inode_num < 32` is mirrored.
# ===========================================================================


# ---------------------------------------------------------------------------
# (4) unlink/remove(f) -> f is ABSENT  (the unlink consequence).
# sys_unlink: _dir_lookup(f) -> found present -> ZERO the matching 32-byte slot
# (`disk[off:off+32] = b'\x00'*32`) -> link-count decrement.  Naming-wise the
# operative step is the slot ZERO.  Scenario: create f at slot 0 (PRESENT:
# inode_num = ino != 0), then unlink ZEROES the whole entry (inode bytes AND
# name byte), then access == _dir_lookup scans applying the inode-num guard.
# A zeroed entry has inode_num == 0, so the guard fails on every slot.
# CONSEQUENCE: the lookup returns -1 -> f is ABSENT after unlink.
#@ requires \str_length(f) == 1
#@ requires ino >= 1 and ino < 32
#@ ensures \result == -1
def unlink_then_access_absent(f: str, ino: int) -> int:
    disk = [0] * 64
    # --- create file f at slot 0: f is PRESENT (inode ino, name f) ---
    disk[0] = ino // 256
    disk[1] = ino % 256
    disk[2] = ord(f[0])
    # --- sys_unlink(f): ZERO the whole matching 32-byte entry (slot 0) ---
    disk[0] = 0
    disk[1] = 0
    disk[2] = 0
    # --- access(f) == _dir_lookup: name match AND inode_num != 0 AND < 32 ---
    found = -1
    name0: str = chr(disk[2])
    ino0 = disk[0] * 256 + disk[1]   # == 0 after unlink -> guard fails
    if name0 == f and ino0 != 0 and ino0 < 32:
        found = ino0
    name1: str = chr(disk[34])
    ino1 = disk[32] * 256 + disk[33]  # == 0 (never written) -> guard fails
    if name1 == f and ino1 != 0 and ino1 < 32:
        found = ino1
    return found                     # == -1 : f is ABSENT after unlink


# (4b) The PRESENT precondition the unlink consumes — f IS resolvable before
# the unlink (so the absence above is a genuine remove, not a vacuous miss).
#@ requires \str_length(f) == 1
#@ requires ino >= 1 and ino < 32
#@ ensures \result == ino
def file_present_before_unlink(f: str, ino: int) -> int:
    disk = [0] * 64
    disk[0] = ino // 256
    disk[1] = ino % 256
    disk[2] = ord(f[0])
    found = -1
    name0: str = chr(disk[2])
    ino0 = disk[0] * 256 + disk[1]
    if name0 == f and ino0 != 0 and ino0 < 32:
        found = ino0
    return found                     # == ino : f is PRESENT before unlink


# ---------------------------------------------------------------------------
# (5) link(a, b) -> b PRESENT and a, b resolve to the SAME inode  (the defining
# property of a hard link).
# sys_link: inode_num = _dir_lookup(a) -> find a free slot -> _write_entry(b,
# slot, inode_num) i.e. write b's name with THE SAME inode_num.  Scenario:
# a is present at slot 0 (inode ino); link writes b at slot 1 carrying THE SAME
# ino; then lookups of a and b each scan and return their inode.
# CONSEQUENCE: lookup(a) == lookup(b) == ino — both names map to one inode.
# This function returns lookup(b); a companion (5b) returns lookup(a); the
# `same-inode` property is `5.result == 5b.result == ino` (both pinned to ino).
#@ requires \str_length(a) == 1
#@ requires \str_length(b) == 1
#@ requires a != b
#@ requires ino >= 1 and ino < 32
#@ ensures \result == ino
def link_b_resolves_to_same_inode(a: str, b: str, ino: int) -> int:
    disk = [0] * 64
    # --- a present at slot 0 (inode ino) ---
    disk[0] = ino // 256
    disk[1] = ino % 256
    disk[2] = ord(a[0])
    # --- sys_link(a, b): write b at the free slot 1 with THE SAME inode ino ---
    disk[32] = ino // 256
    disk[33] = ino % 256
    disk[34] = ord(b[0])
    # --- access(b) == _dir_lookup: return the inode whose name == b ---
    found = -1
    name0: str = chr(disk[2])        # == a, and a != b -> no spurious match
    ino0 = disk[0] * 256 + disk[1]
    if name0 == b and ino0 != 0 and ino0 < 32:
        found = ino0
    name1: str = chr(disk[34])       # == b -> matches at b's own slot
    ino1 = disk[32] * 256 + disk[33]
    if name1 == b and ino1 != 0 and ino1 < 32:
        found = ino1
    return found                     # == ino : b resolves to the SAME inode as a


# (5b) link(a, b) -> a STILL resolves to ino (the original name persists, the
# OTHER half of "same inode").  Together with (5): lookup(a) == lookup(b) == ino.
#@ requires \str_length(a) == 1
#@ requires \str_length(b) == 1
#@ requires a != b
#@ requires ino >= 1 and ino < 32
#@ ensures \result == ino
def link_a_still_resolves(a: str, b: str, ino: int) -> int:
    disk = [0] * 64
    disk[0] = ino // 256
    disk[1] = ino % 256
    disk[2] = ord(a[0])
    disk[32] = ino // 256
    disk[33] = ino % 256
    disk[34] = ord(b[0])
    found = -1
    name0: str = chr(disk[2])        # == a -> matches at a's own slot
    ino0 = disk[0] * 256 + disk[1]
    if name0 == a and ino0 != 0 and ino0 < 32:
        found = ino0
    name1: str = chr(disk[34])       # == b, and b != a -> no spurious match
    ino1 = disk[32] * 256 + disk[33]
    if name1 == a and ino1 != 0 and ino1 < 32:
        found = ino1
    return found                     # == ino : a STILL resolves to ino


# ---------------------------------------------------------------------------
# (6) rename(a, b) -> a ABSENT and b PRESENT, b resolving to a's ORIGINAL inode.
# sys_rename: inode_num = _dir_lookup(a) -> ZERO a's slot -> ZERO any existing
# b slot -> _write_entry(b, free_slot, inode_num) i.e. write b carrying a's
# ORIGINAL inode.  Scenario: a present at slot 0 (inode ino); rename ZEROES
# slot 0 and writes b at slot 1 with THE SAME ino.
# CONSEQUENCE (b PRESENT, same inode): lookup(b) == ino.
#@ requires \str_length(a) == 1
#@ requires \str_length(b) == 1
#@ requires a != b
#@ requires ino >= 1 and ino < 32
#@ ensures \result == ino
def rename_b_present_same_inode(a: str, b: str, ino: int) -> int:
    disk = [0] * 64
    # --- a present at slot 0 (inode ino) ---
    disk[0] = ino // 256
    disk[1] = ino % 256
    disk[2] = ord(a[0])
    # --- sys_rename(a, b): ZERO a's slot 0, write b at slot 1 with same ino ---
    disk[0] = 0
    disk[1] = 0
    disk[2] = 0
    disk[32] = ino // 256
    disk[33] = ino % 256
    disk[34] = ord(b[0])
    # --- access(b) == _dir_lookup ---
    found = -1
    name0: str = chr(disk[2])        # zeroed (chr(0)), ino0 == 0 -> guard fails
    ino0 = disk[0] * 256 + disk[1]
    if name0 == b and ino0 != 0 and ino0 < 32:
        found = ino0
    name1: str = chr(disk[34])       # == b -> matches at b's slot
    ino1 = disk[32] * 256 + disk[33]
    if name1 == b and ino1 != 0 and ino1 < 32:
        found = ino1
    return found                     # == ino : b PRESENT, resolving to a's inode


# (6b) rename(a, b) -> a is ABSENT (a's name no longer resolves).
# CONSEQUENCE (a ABSENT): lookup(a) == -1.
#@ requires \str_length(a) == 1
#@ requires \str_length(b) == 1
#@ requires a != b
#@ requires ino >= 1 and ino < 32
#@ ensures \result == -1
def rename_a_absent(a: str, b: str, ino: int) -> int:
    disk = [0] * 64
    disk[0] = ino // 256
    disk[1] = ino % 256
    disk[2] = ord(a[0])
    # --- sys_rename(a, b): ZERO a's slot, write b at slot 1 ---
    disk[0] = 0
    disk[1] = 0
    disk[2] = 0
    disk[32] = ino // 256
    disk[33] = ino % 256
    disk[34] = ord(b[0])
    # --- access(a) == _dir_lookup: a was zeroed -> guard fails; b's name != a ---
    found = -1
    name0: str = chr(disk[2])        # zeroed -> ino0 == 0 -> guard fails
    ino0 = disk[0] * 256 + disk[1]
    if name0 == a and ino0 != 0 and ino0 < 32:
        found = ino0
    name1: str = chr(disk[34])       # == b, and b != a -> no spurious match
    ino1 = disk[32] * 256 + disk[33]
    if name1 == a and ino1 != 0 and ino1 < 32:
        found = ino1
    return found                     # == -1 : a is ABSENT after rename
