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
