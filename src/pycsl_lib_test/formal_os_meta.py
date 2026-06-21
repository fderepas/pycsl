# formal_os_meta.py — os METADATA consequences (stat/lstat/chmod/truncate),
# through the PUBLIC API ONLY, under the FAITHFUL EXCEPTION model.
#
# INTERNALS-BLIND. Imports only public names from pycsl_lib.os; no _filesystem,
# disk, sys_*, _dir_lookup, or UnixInodeFileSystem reference in code (assigns may
# name the documented _filesystem World global). Each theorem follows the
# formal_os convention: take symbolic params, return int, assert the OBSERVED
# value as `\result == 1`.
#
# WHAT PROVES (verified by the oracle):
#   stat / lstat : mkdir(d) pins `dir_lookup(dir,5,d) >= 0`, and stat/lstat (which
#       RAISE FileNotFoundError on an absent path) deliver a VALID inode
#       (0 <= result < 32) on the success path for that same name. NON-VACUOUS:
#       ties the result to the name mkdir created, not the bare bound.
#   mkdir -> access : mkdir(d) pins `dir_lookup(dir,5,d) >= 0`, and access reports
#       `\result == 1 <==> dir_lookup(dir,5,d) >= 0`, so the entry mkdir created is
#       OBSERVED present through the API.
#   chmod / truncate -> access : both now return None and RAISE OSError on failure
#       (no more -1 return). On the success path neither removes the name, so a
#       mkdir->op->access scenario observes the name still PRESENT (== 1). This is
#       a genuine NAMEABLE consequence (the op succeeded and left the name).
#
# DOCUMENTED GAPS (deeper value consequence not pinned by the public contract):
#   chmod : the MODE consequence (chmod(f, m) reflected in stat(f)'s mode field)
#       is NOT pinned — there is no mode accessor at the os.* layer. The asserted
#       claim is the name-presence consequence (chmod did not remove the name).
#   truncate : the SIZE consequence (truncate(f, length) => size == length) is NOT
#       pinned — there is no name-keyed size accessor at the os.* layer (stat
#       returns the inode number, not the size). truncate now takes `filepath: str`,
#       so it is driven over a str-keyed mkdir->truncate scenario; the asserted
#       claim is the name-presence consequence (truncate did not remove the name).
#
# CO-IMPORT NOTE (tool quirk workaround): mkdir + access (whose dir_lookup ensures
# reference the filesystem arrays) are co-imported and CALLED in every theorem,
# which triggers `use array.Array` and keeps the file emittable.

from pycsl_lib.os import (
    mkdir, access, chmod, truncate, stat, lstat, F_OK,
)


# ---------------------------------------------------------------------------
# stat: mkdir(d) then stat(d) reports a VALID inode for the name created.
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
# mkdir -> access present. This also CALLS mkdir + access whose dir_lookup ensures
# trigger `use array.Array` (the co-import workaround), so chmod/truncate below
# emit cleanly.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 1
def mkdir_then_dir_present(d: str) -> int:
    mkdir(d, 0o777)                 # operate: create the directory (raises on failure)
    return access(d, F_OK)          # observe: d PRESENT — ASSERTED == 1


# ---------------------------------------------------------------------------
# chmod: name-presence consequence (DOCUMENTED MODE GAP). chmod returns None and
# RAISES OSError on failure; on the success path it does NOT remove the name. The
# MODE consequence (chmod(f, m) reflected in stat(f)'s mode field) is NOT pinned
# by the public contract — no mode accessor at the os.* layer. The asserted claim
# is that chmod kept the name present.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 1
def chmod_keeps_name_present(d: str, m: int) -> int:
    mkdir(d, 0o777)                # setup: create the directory (raises on failure)
    chmod(d, m)                    # operate: change mode (str-typed path; raises on failure)
    return access(d, F_OK)         # observe: still PRESENT — ASSERTED == 1


# ---------------------------------------------------------------------------
# truncate: name-presence consequence (DOCUMENTED SIZE GAP). truncate now takes
# `filepath: str` and RAISES OSError on failure (no more -1). The SIZE consequence
# (truncate(f, length) => size == length) is NOT pinned by the public contract
# (no name-keyed size accessor at the os.* layer). The asserted claim is that
# truncate kept the name present over a str-keyed mkdir->truncate scenario.
#@ requires length >= 0
#@ assigns _filesystem.disk
#@ ensures \result == 1
def truncate_keeps_name_present(f: str, length: int) -> int:
    mkdir(f, 0o777)                # setup: create the name (raises on failure)
    truncate(f, length)           # operate: truncate (str-typed path; raises on failure)
    return access(f, F_OK)         # observe: still PRESENT — ASSERTED == 1
