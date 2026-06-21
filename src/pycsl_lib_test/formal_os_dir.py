"""Formal test: os directory/namespace-mutating syscalls — consequence scenarios.

Each theorem is a genuine setup -> operate -> OBSERVE scenario (the shape the
skill's Step 5 prescribes, à la formal_0001's write->read-back): it performs
the target namespace mutation through the PUBLIC os.* API and then calls the
model's real observation primitive (access) on the affected name, asserting the
OBSERVED consequence — not the mutator's own return code.

FAITHFUL EXCEPTION MODEL.  The os.* mutators no longer return -1 on failure:
they RAISE OSError (open raises FileNotFoundError/OSError).  The SUCCESS path is
precisely the non-raising path, on which each mutator's dir_lookup post-state
holds UNCONDITIONALLY.  So the old `if rc != 0: return <vacuous>` guards are
gone — a plain call IS the success path, and the asserted consequence is the
post-state of a mutation that did not raise.

WHAT IS PROVEN.  The genuine functional consequence proves through the public
API for every namespace op:
  - mkdir(d) / makedirs(d) / link(a,b)->b / rename(a,b)->b / symlink(t,l)->l:
    access(name, F_OK) == 1  (PRESENT after create)
  - mkdir(d);rmdir(d) / mkdir(f);unlink(f) / mkdir(f);remove(f) /
    rename(a,b)->a: access(name, F_OK) == 0  (ABSENT after removal/move)

DOCUMENTED GAP.  truncate's deeper consequence (the size field of f's inode ==
length) remains unobservable at the os.* str layer: there is no name-keyed size
accessor (stat returns the inode number, not the size).  truncate now takes a
str path and RAISES on failure, so the strongest NAMEABLE consequence is that
truncate did not remove the name — observed via access (== 1).

Whole-API coverage: mkdir, makedirs, rmdir, unlink, remove, link, rename
(new + old), symlink, truncate.
"""
from pycsl_lib.os import (
    mkdir, makedirs, rmdir, unlink, remove, link, rename, symlink, truncate,
    access,
)

F_OK = 0


# mkdir -> observe PRESENT.
# CONSEQUENCE: after mkdir(d) succeeds (does not raise), access(d, F_OK) reports
# the directory PRESENT (== 1).  Proven through the public API (mkdir's ensures
# pins the name->present link that access reads back).
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 1
def formal_os_mkdir(name: str) -> int:
    mkdir(name, 0o777)               # raises on failure — success path observed
    return access(name, F_OK)        # observe: PRESENT — ASSERTED == 1


# makedirs (nested wrapper) -> observe PRESENT.
# CONSEQUENCE: after makedirs(d) succeeds, access(d, F_OK) reports PRESENT (== 1).
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 1
def formal_os_makedirs(name: str) -> int:
    makedirs(name)                   # raises on failure — success path observed
    return access(name, F_OK)        # observe: PRESENT — ASSERTED == 1


# rmdir -> observe ABSENT.  (the worked example: create -> present -> rmdir -> absent)
# CONSEQUENCE: mkdir(d); rmdir(d); then access(d, F_OK) == 0 (absent).
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0
def formal_os_rmdir(name: str) -> int:
    mkdir(name, 0o777)               # set up: create the directory
    rmdir(name)                      # the REAL removal (raises on failure)
    return access(name, F_OK)        # observe: now ABSENT — ASSERTED == 0


# unlink -> observe ABSENT.
# CONSEQUENCE: mkdir(f); unlink(f); then access(f, F_OK) == 0 (absent).
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0
def formal_os_unlink(name: str) -> int:
    mkdir(name, 0o777)               # set up a name resolvable by access
    unlink(name)                     # the REAL removal (raises on failure)
    return access(name, F_OK)        # observe: now ABSENT — ASSERTED == 0


# remove (alias of unlink) -> observe ABSENT.
# CONSEQUENCE: mkdir(f); remove(f); then access(f, F_OK) == 0 (absent).
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0
def formal_os_remove(name: str) -> int:
    mkdir(name, 0o777)               # set up a name resolvable by access
    remove(name)                     # the REAL removal (raises on failure)
    return access(name, F_OK)        # observe: now ABSENT — ASSERTED == 0


# link -> observe the new name PRESENT.
# CONSEQUENCE: mkdir(a); link(a, b) succeeds => access(b, F_OK) == 1 (the new
# name b now resolves).  (The deeper hard-link identity "a and b share one inode"
# is observable only via stat's inode number — documented gap.)
#@ requires src != dst
#@ assigns _filesystem.disk, _filesystem.fd_open, _filesystem.fd_inode, _filesystem.fd_offset, _filesystem.fd_flags, _filesystem.fd_block, _filesystem.next_fd, _filesystem._mtime_ticks
#@ ensures \result == 1
def formal_os_link(src: str, dst: str) -> int:
    mkdir(src, 0o777)               # set up: a exists
    link(src, dst)                  # the REAL hard link (raises on failure)
    return access(dst, F_OK)        # observe: b now PRESENT — ASSERTED == 1


# rename -> observe new PRESENT.
# CONSEQUENCE: mkdir(a); rename(a, b) => access(b, F_OK) == 1 (b present).
# (The companion consequence access(a) == 0 is formal_os_rename_old_absent.)
#@ requires src != dst
#@ assigns _filesystem.disk, _filesystem.dir
#@ ensures \result == 1
def formal_os_rename(src: str, dst: str) -> int:
    mkdir(src, 0o777)               # set up: a exists
    rename(src, dst)                # the REAL rename (raises on failure)
    return access(dst, F_OK)        # observe: b PRESENT — ASSERTED == 1


# rename -> observe OLD name ABSENT.
# CONSEQUENCE: mkdir(a); rename(a, b) => access(a, F_OK) == 0 (a no longer resolves).
#@ requires src != dst
#@ assigns _filesystem.disk, _filesystem.dir
#@ ensures \result == 0
def formal_os_rename_old_absent(src: str, dst: str) -> int:
    mkdir(src, 0o777)               # set up: a exists
    rename(src, dst)                # the REAL rename (raises on failure)
    return access(src, F_OK)        # observe: a now ABSENT — ASSERTED == 0


# symlink -> observe the link name PRESENT.
# CONSEQUENCE: symlink(t, l) => access(l, F_OK) == 1 (the link name resolves).
# (readlink content is not observable at the os.* str layer — documented gap.)
#@ requires target != linkpath
#@ assigns _filesystem.disk
#@ ensures \result == 1
def formal_os_symlink(target: str, linkpath: str) -> int:
    symlink(target, linkpath)       # the REAL symlink (raises on failure)
    return access(linkpath, F_OK)   # observe: l PRESENT — ASSERTED == 1


# truncate -> observe the name still PRESENT (DOCUMENTED SIZE GAP).
# CONSEQUENCE we want: after create+truncate(f, n), the size field of f's inode
# == n.  UNPROVABLE: no name-keyed size observation primitive is exposed at the
# os.* layer (stat returns the inode number, not the size).  truncate now takes a
# str path and RAISES on failure, so the strongest NAMEABLE consequence is that
# truncate did not remove the name — observed via access (== 1).
#@ requires length >= 0
#@ assigns _filesystem.disk
#@ ensures \result == 1
def formal_os_truncate(name: str, length: int) -> int:
    mkdir(name, 0o777)              # set up: the name resolves
    truncate(name, length)         # the REAL truncate (raises on failure)
    return access(name, F_OK)      # observe: still PRESENT — ASSERTED == 1
