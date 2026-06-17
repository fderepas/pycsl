# formal_os_meta.py — os METADATA consequences (stat/lstat/chmod/truncate),
# through the PUBLIC API ONLY.
#
# INTERNALS-BLIND. Imports only public names from pure_lib.os; no _filesystem,
# disk, sys_*, _dir_lookup, or UnixInodeFileSystem reference in code or contracts.
# Each theorem follows the formal_os convention: take symbolic params, return int,
# guard the mutator return codes, and assert the OBSERVED value as `\result == 1`.
#
# WHAT PROVES (verified by the oracle):
#   stat / lstat : mkdir(d) pins `dir_lookup(disk,5,d) >= 0`, and stat/lstat's
#       path-link ensures then deliver a VALID inode (0 <= result < 32) for that
#       same name. The functional consequence "after creating d, stat/lstat
#       reports a valid inode for d" is ENTAILED by the public contracts (NON-
#       VACUOUS: ties the result to the name mkdir created, not the bare bound).
#   mkdir -> access : mkdir(d) pins `\result == 0 ==> dir_lookup(disk,5,d) >= 0`,
#       and access reports `\result == 1 <==> dir_lookup(disk,5,d) >= 0`, so the
#       entry mkdir created is OBSERVED present through the API.
#
# DOCUMENTED GAPS (return-code-only contracts; deeper consequence not pinned):
#   chmod : public contract is `\result == 0 or -1` (return-code only); chmod
#       `assigns _filesystem.disk` with no dir_lookup frame. The MODE consequence
#       (chmod(f, m) reflected in stat(f)'s mode field) is NOT pinned by the public
#       contract (no mode accessor at the os.* layer). chmod takes `filepath: str`,
#       so it is called with a str path over a mkdir->chmod scenario; the asserted
#       claim is the documented return-code bound.
#   truncate : public contract is `\result == 0 or -1` (return-code only), no size
#       post-state. The SIZE consequence (truncate(f, length) => size == length)
#       is NOT pinned by the public contract. truncate leaves its `filepath` param
#       un-annotated, so the emitted stub types it `int`; it is called with an int
#       and the asserted claim is the documented return-code bound.
#
# CO-IMPORT NOTE (tool quirk workaround): chmod/truncate carry only return-code
# ensures and pull in array-typed helper predicates without an array-typed
# `ensures`, which can make the emitter skip `use array.Array` and fail at L3-tc
# with `unbound type symbol 'array'`. We co-import mkdir + access (whose dir_lookup
# ensures reference the filesystem arrays) and CALL them in theorems below, which
# triggers `use array.Array` and keeps the file emittable.

from pure_lib.os import (
    mkdir, access, chmod, truncate, stat, lstat, F_OK,
)


# ---------------------------------------------------------------------------
# stat: mkdir(d) then stat(d) reports a VALID inode for the name created.
#@ requires True
#@ ensures \result == 1
def stat_after_mkdir_valid_inode(d: str) -> int:
    rc = mkdir(d, 0o777)            # operate: create the directory
    if rc != 0:
        return 1                    # mkdir failed: not the case under test (guarded)
    ino = stat(d)                   # observe: stat resolves the name mkdir created
    if ino >= 0 and ino < 32:       # ASSERTED: a valid inode
        return 1
    return 0


# ---------------------------------------------------------------------------
# lstat: like stat (no symlink follow in this single-level model); same chain.
#@ requires True
#@ ensures \result == 1
def lstat_after_mkdir_valid_inode(d: str) -> int:
    rc = mkdir(d, 0o777)            # operate: create the directory
    if rc != 0:
        return 1                    # mkdir failed: not the case under test (guarded)
    ino = lstat(d)                  # observe: lstat resolves the name mkdir created
    if ino >= 0 and ino < 32:       # ASSERTED: a valid inode
        return 1
    return 0


# ---------------------------------------------------------------------------
# mkdir -> access present. This also CALLS mkdir + access whose dir_lookup ensures
# trigger `use array.Array` (the co-import workaround), so chmod/truncate below
# emit cleanly.
#@ requires True
#@ ensures \result == 1
def mkdir_then_dir_present(d: str) -> int:
    rc = mkdir(d, 0o777)            # operate: create the directory
    if rc != 0:
        return 1                    # mkdir failed: not the case under test (guarded)
    return access(d, F_OK)          # observe: d PRESENT — ASSERTED == 1


# ---------------------------------------------------------------------------
# chmod: return-code bound (DOCUMENTED GAP). chmod takes `filepath: str`, so it is
# called with a str path over a mkdir->chmod scenario. The MODE consequence
# (chmod(f, m) reflected in stat(f)'s mode field) is NOT pinned by the public
# contract — no mode accessor at the os.* layer, and chmod assigns disk with no
# dir_lookup frame. The asserted claim is the documented return-code bound.
#@ requires True
#@ ensures \result == 1
def chmod_returns_code(d: str, m: int) -> int:
    rc = mkdir(d, 0o777)           # setup: create the directory
    if rc != 0:
        return 1                   # mkdir failed: not the case under test (guarded)
    r = chmod(d, m)                # operate: change mode (str-typed path)
    if r == 0 or r == -1:          # ASSERTED: documented return-code bound
        return 1
    return 0


# ---------------------------------------------------------------------------
# truncate: return-code bound (DOCUMENTED GAP). truncate's `filepath` param is
# un-annotated, so the emitted stub types it `int`; it is called with an int. The
# SIZE consequence (truncate(f, length) => size == length) is NOT pinned by the
# public contract (return-code only, no size post-state). The asserted claim is
# the documented return-code bound.
#@ requires True
#@ ensures \result == 1
def truncate_returns_code(f: int, length: int) -> int:
    rc = truncate(f, length)       # operate: truncate (int-typed path stub)
    if rc == 0 or rc == -1:        # ASSERTED: documented return-code bound
        return 1
    return 0
