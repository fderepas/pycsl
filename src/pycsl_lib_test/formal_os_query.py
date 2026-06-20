# formal_os_query.py — os READ-ONLY OBSERVERS (stat, lstat, fstat, readlink,
# access, listdir, scandir, chmod, getcwd, getpid), through the PUBLIC API ONLY.
#
# INTERNALS-BLIND. Imports only public names from pycsl_lib.os; no _filesystem,
# disk, sys_*, _dir_lookup, or UnixInodeFileSystem reference in code or contracts.
# Each theorem follows the formal_os convention: take symbolic params, return int,
# guard the mutator return codes, and assert the OBSERVED value as `\result == 1`.
#
# A consequence test for an observer establishes a KNOWN object via the public
# mutators and then asserts the observer reports it correctly (setup -> operate ->
# observe), NOT the observer's own return code.
#
# WHAT PROVES (verified by the oracle, not by assertion):
#   stat / lstat : mkdir(d) pins `dir_lookup(disk,5,d) >= 0`; stat/lstat's
#       path-link ensures then deliver a VALID inode (0 <= result < 32) for that
#       same name. The functional consequence "after creating d, stat/lstat
#       reports a valid inode for d" is ENTAILED by the public contracts.
#   access : mkdir(d) => access(d, F_OK) == 1 (present); mkdir(d); rmdir(d) =>
#       access(d, F_OK) == 0 (absent). Both chain through the dir_lookup view.
#   readlink : symlink(src, dst) then readlink(dst) returns a block in range or
#       -1. readlink has NO content-returning observer, so the geometry bound over
#       the symlink->read chain is the honest claim (see NOT-CLAIM below).
#   fstat : geometry bound over a symbolic open fd (-1 or 0 <= result < 32). The
#       open->fstat inode-RESOLUTION consequence is covered in formal_os_fdchain.py;
#       here, over a symbolic fd, the inode-range bound is the honest claim.
#   listdir / scandir : \length(\result) <= 16 (the model caps entries at 16).
#   getcwd : == 0 (root inode; the model exposes no chdir to round-trip against,
#       so this honestly asserts the modeled constant, not a chdir consequence).
#   getpid : == 1 (the modeled pid; a constant, not a mutating consequence).
#
# DOCUMENTED GAPS (strongest NAMEABLE form kept; deeper consequence not pinned):
#   chmod : contract is return-code-only (`\result == 0 or -1`); the deeper
#       consequence "chmod(f, m) reflected in stat(f)'s mode field" is NOT pinned
#       by the public contract (no mode accessor at the os.* layer). The theorem
#       asserts the documented return-code bound over a mkdir->chmod scenario.
#   readlink : the target-VALUE consequence ("readlink(dst) == the target
#       symlink stored") is NOT a claim — readlink's contract is geometry-only and
#       does not discriminate the success target value; the stored bytes are
#       unmodeled. The range bound over the chain is the strongest honest claim.
#   fstat : the inode-VALUE consequence over a symbolic fd is not pinned here (it
#       requires the open site to bind fd_inode); that is the formal_os_fdchain.py
#       theorem. Here the geometry bound is the honest claim.

from pycsl_lib.os import (
    stat, lstat, fstat, readlink, access, listdir, scandir, chmod,
    getcwd, getpid, mkdir, rmdir, symlink, F_OK,
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
# fstat: geometry bound over a symbolic open fd. The open->fstat inode-RESOLUTION
# consequence is covered in formal_os_fdchain.py; over a symbolic fd the honest
# claim is the inode-range bound (-1 for a bad fd, else a valid inode).
#@ requires fd >= 0
#@ ensures \result == 1
def fstat_geometry_bound(fd: int) -> int:
    ino = fstat(fd)                 # observe: inode by fd
    if ino == -1 or (ino >= 0 and ino < 32):  # ASSERTED: -1 or valid inode
        return 1
    return 0


# ---------------------------------------------------------------------------
# readlink: symlink(src, dst) then readlink(dst) returns a block in range or -1.
# NOT a claim: readlink(dst) == the target symlink stored (geometry-only contract).
#@ requires src != dst
#@ ensures \result == 1
def readlink_after_symlink_in_range(src: str, dst: str) -> int:
    rc = symlink(src, dst)          # operate: create the symbolic link
    if rc != 0:
        return 1                    # symlink failed: not the case under test (guarded)
    blk = readlink(dst)             # observe: read the link's stored target block
    if blk == -1 or (blk >= 0 and blk < 256):  # ASSERTED: -1 or block in range
        return 1
    return 0


# ---------------------------------------------------------------------------
# access (presence): mkdir(d) => access(d, F_OK) == 1.
#@ requires True
#@ ensures \result == 1
def access_present_after_mkdir(d: str) -> int:
    rc = mkdir(d, 0o777)            # operate: create the directory
    if rc != 0:
        return 1                    # mkdir failed: not the case under test (guarded)
    return access(d, F_OK)          # observe: d PRESENT — ASSERTED == 1


# ---------------------------------------------------------------------------
# access (absence): mkdir(d); rmdir(d) => access(d, F_OK) == 0.
#@ requires True
#@ ensures \result == 1
def access_absent_after_rmdir(d: str) -> int:
    rc = mkdir(d, 0o777)            # setup: create the directory
    if rc != 0:
        return 1                    # mkdir failed: not the case under test (guarded)
    rc2 = rmdir(d)                  # operate: remove it
    if rc2 != 0:
        return 1                    # rmdir failed: not the case under test (guarded)
    if access(d, F_OK) == 0:        # observe: d ABSENT — ASSERTED == 0
        return 1
    return 0


# ---------------------------------------------------------------------------
# listdir: the model caps directory entries at 16, so the listing length <= 16.
# NOTE: listdir's `filepath` param is un-annotated (default '.'), so the emitted
# stub types it `int`; call it with an int per the stub's type.
#@ requires True
#@ ensures \result == 1
def listdir_length_bound(d: int) -> int:
    names = listdir(d)             # observe: list directory contents
    if len(names) <= 16:           # ASSERTED: <= 16
        return 1
    return 0


# ---------------------------------------------------------------------------
# scandir: same cap as listdir. Same int-typed path as listdir (un-annotated).
#@ requires True
#@ ensures \result == 1
def scandir_length_bound(d: int) -> int:
    items = scandir(d)             # observe: scan directory entries
    if len(items) <= 16:           # ASSERTED: <= 16
        return 1
    return 0


# ---------------------------------------------------------------------------
# chmod: return-code bound (DOCUMENTED GAP). The deeper consequence — chmod(f, m)
# reflected in stat(f)'s mode field — is NOT pinned by the public contract (no
# mode accessor at the os.* layer). Asserted over a mkdir->chmod scenario.
#@ requires True
#@ ensures \result == 1
def chmod_returns_code(d: str, m: int) -> int:
    rc = mkdir(d, 0o777)           # setup: create the directory
    if rc != 0:
        return 1                   # mkdir failed: not the case under test (guarded)
    r = chmod(d, m)                # operate: change mode
    if r == 0 or r == -1:          # ASSERTED: documented return-code bound
        return 1
    return 0


# ---------------------------------------------------------------------------
# getcwd: the model exposes no chdir to round-trip against; getcwd is the CONSTANT
# root inode (0). Honestly asserts the modeled constant, not a chdir consequence.
#@ requires True
#@ ensures \result == 1
def getcwd_root_inode() -> int:
    if getcwd() == 0:              # ASSERTED: root inode 0
        return 1
    return 0


# ---------------------------------------------------------------------------
# getpid: the modeled pid (1). A constant; no mutating consequence to round-trip.
#@ requires True
#@ ensures \result == 1
def getpid_constant() -> int:
    if getpid() == 1:             # ASSERTED: pid 1
        return 1
    return 0
