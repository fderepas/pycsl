# formal_os_query.py — os READ-ONLY OBSERVERS (stat, lstat, fstat, readlink,
# access, listdir, scandir, chmod, getcwd, getpid), through the PUBLIC API ONLY,
# under the FAITHFUL EXCEPTION model.
#
# INTERNALS-BLIND. Imports only public names from pycsl_lib.os; no _filesystem,
# disk, sys_*, _dir_lookup, or UnixInodeFileSystem reference in code (assigns may
# name the documented _filesystem World global). Each theorem follows the
# formal_os convention: take symbolic params, return int, assert the OBSERVED
# value as `\result == 1`.
#
# A consequence test for an observer establishes a KNOWN object via the public
# mutators and then asserts the observer reports it correctly (setup -> operate ->
# observe), NOT the observer's own return code.
#
# WHAT PROVES (verified by the oracle, not by assertion):
#   stat / lstat : mkdir(d) pins `dir_lookup(dir,5,d) >= 0`; stat/lstat (which
#       RAISE FileNotFoundError when the path is absent) deliver a VALID inode
#       (0 <= result < 32) on the success path for that same name.
#   access : mkdir(d) => access(d, F_OK) == 1 (present); mkdir(d); rmdir(d) =>
#       access(d, F_OK) == 0 (absent). Both chain through the dir_lookup view.
#   readlink : symlink(src, dst) then readlink(dst) returns a block in range.
#       readlink (which RAISES OSError on failure) has NO content-returning
#       observer, so the geometry bound over the symlink->read chain is the
#       honest claim (see NOT-CLAIM below).
#   fstat : geometry bound over a symbolic open fd. fstat RAISES OSError on a
#       bad/closed fd; on the success path it returns a valid inode (0 <= r < 32).
#   listdir / scandir : on a freshly mkdir'd directory, \length(\result) <= 16
#       (the model caps entries at 16). listdir/scandir RAISE OSError on an
#       absent/not-a-dir path, so we mkdir(d) first.
#   getcwd : == 0 (root inode; the model exposes no chdir to round-trip against).
#   getpid : == 1 (the modeled pid; a constant).
#
# DOCUMENTED GAPS (strongest NAMEABLE form kept; deeper consequence not pinned):
#   chmod : returns None and RAISES OSError on failure; on success it leaves the
#       name present (assigns disk only, no dir_lookup removal). The deeper
#       consequence "chmod(f, m) reflected in stat(f)'s mode field" is NOT pinned
#       by the public contract (no mode accessor at the os.* layer). The theorem
#       observes the NAMEABLE consequence: chmod does not remove the name, so
#       access(f, F_OK) == 1 after a mkdir->chmod scenario.
#   readlink : the target-VALUE consequence ("readlink(dst) == the target
#       symlink stored") is NOT a claim — readlink's contract is geometry-only and
#       the stored bytes are unmodeled. The range bound over the chain is the
#       strongest honest claim.
#   fstat : the inode-VALUE consequence over a symbolic fd is not pinned here (it
#       requires the open site to bind fd_inode); that is the formal_os_fdchain.py
#       theorem. Here the geometry bound is the honest claim.

from pycsl_lib.os import (
    stat, lstat, fstat, readlink, access, listdir, scandir, chmod,
    getcwd, getpid, mkdir, rmdir, symlink, F_OK,
)


# ---------------------------------------------------------------------------
# stat: mkdir(d) then stat(d) reports a VALID inode for the name created.
# stat RAISES on an absent path; on the success path it returns a valid inode.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 1
def stat_after_mkdir_valid_inode(d: str) -> int:
    mkdir(d, 0o777)                 # operate: create the directory (raises on failure)
    ino = stat(d)                   # observe: stat resolves the name mkdir created
    if ino >= 0 and ino < 32:       # ASSERTED: a valid inode
        return 1
    return 0


# ---------------------------------------------------------------------------
# lstat: like stat (no symlink follow in this single-level model); same chain.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 1
def lstat_after_mkdir_valid_inode(d: str) -> int:
    mkdir(d, 0o777)                 # operate: create the directory (raises on failure)
    ino = lstat(d)                  # observe: lstat resolves the name mkdir created
    if ino >= 0 and ino < 32:       # ASSERTED: a valid inode
        return 1
    return 0


# ---------------------------------------------------------------------------
# fstat: geometry bound over a symbolic open fd. fstat RAISES OSError on a bad
# fd; on the success path it returns a valid inode (0 <= r < 32).
#@ requires fd >= 0
#@ assigns \nothing
#@ ensures \result == 1
def fstat_geometry_bound(fd: int) -> int:
    ino = fstat(fd)                 # observe: inode by fd (raises on bad fd)
    if ino >= 0 and ino < 32:       # ASSERTED: valid inode
        return 1
    return 0


# ---------------------------------------------------------------------------
# readlink: symlink(src, dst) then readlink(dst) returns a block in range.
# NOT a claim: readlink(dst) == the target symlink stored (geometry-only contract).
#@ requires src != dst
#@ assigns _filesystem.disk
#@ ensures \result == 1
def readlink_after_symlink_in_range(src: str, dst: str) -> int:
    symlink(src, dst)               # operate: create the symbolic link (raises on failure)
    blk = readlink(dst)             # observe: read the link's stored target block
    if blk >= 0 and blk < 256:      # ASSERTED: block in range
        return 1
    return 0


# ---------------------------------------------------------------------------
# access (presence): mkdir(d) => access(d, F_OK) == 1.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 1
def access_present_after_mkdir(d: str) -> int:
    mkdir(d, 0o777)                 # operate: create the directory (raises on failure)
    return access(d, F_OK)          # observe: d PRESENT — ASSERTED == 1


# ---------------------------------------------------------------------------
# access (absence): mkdir(d); rmdir(d) => access(d, F_OK) == 0.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 1
def access_absent_after_rmdir(d: str) -> int:
    mkdir(d, 0o777)                 # setup: create the directory (raises on failure)
    rmdir(d)                        # operate: remove it (raises on failure)
    if access(d, F_OK) == 0:        # observe: d ABSENT — ASSERTED == 0
        return 1
    return 0


# ---------------------------------------------------------------------------
# listdir: the model caps directory entries at 16, so the listing length <= 16.
# listdir RAISES OSError on an absent/not-a-dir path, so we mkdir(d) first.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 1
def listdir_length_bound(d: str) -> int:
    mkdir(d, 0o777)                # setup: create a directory to list
    names = listdir(d)             # observe: list directory contents (raises if absent)
    if len(names) <= 16:           # ASSERTED: <= 16
        return 1
    return 0


# ---------------------------------------------------------------------------
# scandir: same cap as listdir. Same str path; mkdir(d) first (raises if absent).
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 1
def scandir_length_bound(d: str) -> int:
    mkdir(d, 0o777)                # setup: create a directory to scan
    items = scandir(d)             # observe: scan directory entries (raises if absent)
    if len(items) <= 16:           # ASSERTED: <= 16
        return 1
    return 0


# ---------------------------------------------------------------------------
# chmod: chmod returns None and RAISES OSError on failure. The deeper consequence
# — chmod(f, m) reflected in stat(f)'s mode field — is NOT pinned by the public
# contract (no mode accessor at the os.* layer; DOCUMENTED GAP). The NAMEABLE
# consequence is that chmod does NOT remove the name: after mkdir->chmod,
# access(f, F_OK) == 1.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 1
def chmod_keeps_name_present(d: str, m: int) -> int:
    mkdir(d, 0o777)                # setup: create the directory (raises on failure)
    chmod(d, m)                    # operate: change mode (raises on failure)
    return access(d, F_OK)         # observe: still PRESENT — ASSERTED == 1


# ---------------------------------------------------------------------------
# getcwd: the model exposes no chdir to round-trip against; getcwd is the CONSTANT
# root inode (0). Honestly asserts the modeled constant, not a chdir consequence.
#@ requires True
#@ assigns \nothing
#@ ensures \result == 1
def getcwd_root_inode() -> int:
    if getcwd() == 0:              # ASSERTED: root inode 0
        return 1
    return 0


# ---------------------------------------------------------------------------
# getpid: the modeled pid (1). A constant; no mutating consequence to round-trip.
#@ requires True
#@ assigns \nothing
#@ ensures \result == 1
def getpid_constant() -> int:
    if getpid() == 1:             # ASSERTED: pid 1
        return 1
    return 0
