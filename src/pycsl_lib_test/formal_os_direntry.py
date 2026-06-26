# formal_os_direntry.py — os DirEntry CONSEQUENCE tests — PUBLIC API ONLY.
#
# STATUS: PROVEN (gap-4 partially closed). DirEntry was UNTESTABLE through
# the public API because __init__ took `fs` (the module global
# UnixInodeFileSystem) as a parameter, and PyCSL's aliasing rule prohibits
# passing a module global as an argument in a formal-test driver. Strategy C
# applied: `fs` removed from the constructor; the is_dir/is_file/is_symlink
# methods now reach the module-level `_filesystem` directly (as listdir/
# scandir/walk already do). DirEntry is now CONSTRUCTIBLE.
#
# Strategy D applied for the TEST HOOK: free-function wrappers
# (dirent_is_dir / dirent_is_file / dirent_is_symlink / dirent_is_junction)
# delegate to a freshly constructed DirEntry. The formal-test driver imports
# THESE functions, not the DirEntry class — the class-import path emits
# ill-typed module stubs (see
# bugs-to-report/20260623-1600-direntry-class-import.md), whereas function
# imports materialize `_filesystem` correctly.
#
# PROVEN CONSEQUENCES (zero TCB, body-faithful):
#   - The -1 sentinel inode: is_dir / is_file / is_symlink all return 0
#     (the out-of-range early-exit, now pinned by
#     `(inode_num < 0 or inode_num >= 32) ==> \result == 0`).
#   - is_junction: always returns 0 (the model has no junctions).
#   - The range bound {0,1} for is_dir on a valid inode.
#
# REMAINING VALUE GAP (open, logged):
#   The value link "is_dir() == 1 for a type-2 inode" is NOT pinned by the
#   contract — the methods call _filesystem._read_inode internally and
#   branch on inode[2] (the type field), but _read_inode's contract exposes
#   only the SIZE field (\result[0] == inode_size(...)), not the TYPE field.
#   Pinning the type link requires an `inode_type` logic function in the
#   UIFS preamble (a tooling change). Until then "mkdir(d); dirent_is_dir(d,
#   ino) == 1" stays Unknown — an honest GAP, not a trusted "done".

from pycsl_lib.os import (
    dirent_is_dir, dirent_is_file, dirent_is_symlink, dirent_is_junction,
)


# (1) is_dir — CONSEQUENCE: the -1 sentinel inode yields 0 (the out-of-range
# early-exit). Non-vacuous: a method ignoring the range guard would return 1.
#@ requires True
#@ assigns \nothing
#@ ensures \result == 1
def direntry_is_dir_sentinel() -> int:
    r = dirent_is_dir("sentinel", -1)
    if r == 0:
        return 1
    return 0


# (2) is_file — CONSEQUENCE: the -1 sentinel inode yields 0.
#@ requires True
#@ assigns \nothing
#@ ensures \result == 1
def direntry_is_file_sentinel() -> int:
    r = dirent_is_file("sentinel", -1)
    if r == 0:
        return 1
    return 0


# (3) is_symlink — CONSEQUENCE: the -1 sentinel inode yields 0.
#@ requires True
#@ assigns \nothing
#@ ensures \result == 1
def direntry_is_symlink_sentinel() -> int:
    r = dirent_is_symlink("sentinel", -1)
    if r == 0:
        return 1
    return 0


# (4) is_junction — CONSEQUENCE: always returns 0 (the model has no
# junctions). Non-vacuous: a method returning 1 would fail. Constructed
# with a valid root inode (0) to exercise the non-sentinel path too.
#@ requires True
#@ assigns \nothing
#@ ensures \result == 1
def direntry_is_junction_zero() -> int:
    r = dirent_is_junction("root", 0)
    if r == 0:
        return 1
    return 0


# (5) is_dir — CONSEQUENCE: the range bound {0,1} holds for a valid inode.
# Non-vacuous: a method returning 2 would fail.
#@ requires True
#@ assigns \nothing
#@ ensures \result == 1
def direntry_is_dir_range() -> int:
    r = dirent_is_dir("root", 0)
    if r == 0 or r == 1:
        return 1
    return 0
