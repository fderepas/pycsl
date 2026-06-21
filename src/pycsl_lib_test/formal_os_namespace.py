# formal_os_namespace.py — os NAMESPACE consequences, through the PUBLIC API ONLY.
#
# This file CALLS THE REAL PUBLIC API the way a caller does — it imports
# `mkdir`, `rmdir`, `unlink`, `link`, `rename`, `access`, `F_OK` from
# pycsl_lib.os and drives a setup -> operate -> OBSERVE scenario, asserting the
# observation's promised post-state. There is NO `disk`, NO `_dir_lookup`, NO
# `sys_*`, NO `UnixInodeFileSystem(...)`, NO hand-written dirent bytes.
#
# FAITHFUL EXCEPTION MODEL. The namespace mutators no longer return -1 on
# failure: they RAISE OSError. The SUCCESS path is precisely the non-raising
# path, on which each mutator's dir_lookup post-state holds UNCONDITIONALLY:
#   mkdir/link/rename(new): dir_lookup(dir, 5, name) >= 0   (present after)
#   rmdir/unlink/rename(old): dir_lookup(dir, 5, name) < 0  (absent after)
# `access`'s contract is (\result == 1) <==> dir_lookup(dir, 5, name) >= 0, so
# the observer reflects the mutator's post-state and each consequence PROVES
# through the API. (Under the old -1 model these were guarded by `if rc != 0`
# and reported Unknown; the strengthened raise-model contracts make them green.)
#
# DO NOT make these green by simulating, by weakening to the observer's own
# return-code disjunction, or by touching internals.

from pycsl_lib.os import (
    mkdir, rmdir, unlink, link, rename, access, F_OK,
)

# NOTE on observers used here. We observe presence/absence with `access`, whose
# path param is annotated `str`. access does NOT raise (returns 0/1), so it is
# the faithful observer for the ABSENT consequence: on an absent name it simply
# returns 0 rather than raising.


# ---------------------------------------------------------------------------
# (1) mkdir(d) -> d is PRESENT.
# Create d via the REAL mkdir (raises on failure), then OBSERVE d via the REAL
# access. CONSEQUENCE: access reports PRESENT (== 1) after mkdir.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 1
def mkdir_then_access_present(d: str) -> int:
    mkdir(d, 0o777)                 # the REAL syscall (raises on failure)
    return access(d, F_OK)          # observe: now PRESENT — ASSERTED == 1


# ---------------------------------------------------------------------------
# (2) mkdir(d) then rmdir(d) -> d is ABSENT again.
# Create d, then remove it via the REAL rmdir, then OBSERVE via the REAL access.
# CONSEQUENCE: access reports ABSENT (== 0) after rmdir.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0
def rmdir_then_access_absent(d: str) -> int:
    mkdir(d, 0o777)                 # set up: create the directory
    rmdir(d)                        # the REAL removal (raises on failure)
    return access(d, F_OK)          # observe: now ABSENT — ASSERTED == 0


# ---------------------------------------------------------------------------
# (3) unlink(f) -> f is ABSENT.
# Create f, then unlink via the REAL unlink, then OBSERVE via the REAL access.
# CONSEQUENCE: access reports ABSENT (== 0) after unlink.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0
def unlink_then_access_absent(f: str) -> int:
    mkdir(f, 0o777)                 # set up a name f resolvable by access
    unlink(f)                       # the REAL removal (raises on failure)
    return access(f, F_OK)          # observe: now ABSENT — ASSERTED == 0


# ---------------------------------------------------------------------------
# (4) The PRESENT precondition a removal consumes — f IS observable BEFORE the
# removal (so the absence theorems above are a genuine remove, not a vacuous
# miss against a never-present name). Create f, then OBSERVE via the REAL access.
# CONSEQUENCE: access reports PRESENT (== 1) right after mkdir.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 1
def file_present_after_mkdir(f: str) -> int:
    mkdir(f, 0o777)                 # the REAL syscall (raises on failure)
    return access(f, F_OK)          # observe: PRESENT — ASSERTED == 1


# ---------------------------------------------------------------------------
# (5) link(a, b) -> b is PRESENT (hard-link semantics: the new name resolves).
# Create a, then link a -> b via the REAL link, then OBSERVE b via the REAL access.
# CONSEQUENCE: access(b, F_OK) reports PRESENT (== 1) after link — b now resolves.
# (The deeper hard-link identity "a and b share one inode" can only be observed
# through stat's inode number; access expresses PRESENT but not the shared inode.)
#@ requires a != b
#@ assigns _filesystem.disk, _filesystem.fd_open, _filesystem.fd_inode, _filesystem.fd_offset, _filesystem.fd_flags, _filesystem.fd_block, _filesystem.next_fd, _filesystem._mtime_ticks
#@ ensures \result == 1
def link_then_b_present(a: str, b: str) -> int:
    mkdir(a, 0o777)                 # set up: a exists
    link(a, b)                      # the REAL hard link (raises on failure)
    return access(b, F_OK)          # observe: b PRESENT — ASSERTED == 1


# ---------------------------------------------------------------------------
# (6a) rename(a, b) -> b is PRESENT.
# Create a, rename a -> b via the REAL rename, then OBSERVE b via the REAL access.
# CONSEQUENCE: access(b, F_OK) reports PRESENT (== 1) after rename.
#@ requires a != b
#@ assigns _filesystem.disk, _filesystem.dir
#@ ensures \result == 1
def rename_then_b_present(a: str, b: str) -> int:
    mkdir(a, 0o777)                 # set up: a exists
    rename(a, b)                    # the REAL rename (raises on failure)
    return access(b, F_OK)          # observe: b PRESENT — ASSERTED == 1


# ---------------------------------------------------------------------------
# (6b) rename(a, b) -> a is ABSENT (the old name no longer resolves).
# Create a, rename a -> b via the REAL rename, then OBSERVE a via the REAL access.
# CONSEQUENCE: access(a, F_OK) reports ABSENT (== 0) after rename.
#@ requires a != b
#@ assigns _filesystem.disk, _filesystem.dir
#@ ensures \result == 0
def rename_then_a_absent(a: str, b: str) -> int:
    mkdir(a, 0o777)                 # set up: a exists
    rename(a, b)                    # the REAL rename (raises on failure)
    return access(a, F_OK)          # observe: a now ABSENT — ASSERTED == 0
