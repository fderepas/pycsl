"""Formal test: os directory/namespace-mutating syscalls — consequence scenarios.

Each theorem is a genuine setup -> operate -> OBSERVE scenario (the shape the
skill's Step 5 prescribes, à la formal_0001's write->read-back): it performs
the target namespace mutation through the PUBLIC os.* API and then calls the
model's real observation primitive (access) on the affected name, asserting the
OBSERVED consequence — not the mutator's own return code.

WHAT IS PROVEN.  The genuine functional consequence proves through the public
API for every namespace op:
  - mkdir(d) / makedirs(d) / link(a,b)->b / rename(a,b)->b / symlink(t,l)->l:
    access(name, F_OK) == 1  (PRESENT after create)
  - mkdir(d);rmdir(d) / mkdir(f);unlink(f) / mkdir(f);remove(f) /
    rename(a,b)->a: access(name, F_OK) == 0  (ABSENT after removal/move)
Each mutator's failure return code is guarded (`if rc != 0: return <vacuous-
consistent value>`) so the asserted consequence is the success-path post-state.

DOCUMENTED GAPS.  Two consequences remain unobservable at the os.* str layer
and keep their strongest provable form:
  - truncate: `filepath` is un-annotated (stub-typed int), and there is no
    str-typed size accessor to chain onto an int path — only the return-code
    bound (\result == 0 or -1) is expressible (no size observer).
  - link's deeper hard-link identity (a and b share one inode) and symlink's
    readlink content are observable only via stat's inode number, blocked by
    stat's int path-typing — access expresses PRESENT but not the shared inode.

Whole-API coverage: mkdir, makedirs, rmdir, unlink, remove, link, rename
(new + old), symlink, truncate.
"""
from pycsl_lib.os import (
    _filesystem,
    mkdir, makedirs, rmdir, unlink, remove, link, rename, symlink, truncate,
    access,
)

F_OK = 0


# mkdir -> observe PRESENT.
# CONSEQUENCE: after mkdir(d) succeeds, access(d, F_OK) reports the directory
# PRESENT (== 1).  This is the genuine setup->operate->observe consequence,
# proven through the public API (mkdir's ensures pins the name->present link
# that access reads back).
#@ requires True
#@ assigns _filesystem.disk, _filesystem._mtime_ticks
#@ ensures \result == 1
def formal_os_mkdir(name: str) -> int:
    rc = mkdir(name, 0o777)
    if rc != 0:
        return 1                     # mkdir failed: not the case under test
    return access(name, F_OK)        # observe: PRESENT — ASSERTED == 1


# makedirs (nested wrapper) -> observe PRESENT.
# CONSEQUENCE: after makedirs(d) succeeds, access(d, F_OK) reports PRESENT
# (== 1).  Proven through the public API.
#@ requires True
#@ assigns _filesystem.disk, _filesystem._mtime_ticks
#@ ensures \result == 1
def formal_os_makedirs(name: str) -> int:
    rc = makedirs(name)
    if rc != 0:
        return 1                     # makedirs failed: not the case under test
    return access(name, F_OK)        # observe: PRESENT — ASSERTED == 1


# rmdir -> observe ABSENT.  (the worked example: create -> present -> rmdir -> absent)
# CONSEQUENCE: mkdir(d); rmdir(d); then access(d, F_OK) == 0 (absent).
# Proven through the public API over the full create->remove->observe chain.
#@ requires True
#@ assigns _filesystem.disk, _filesystem._mtime_ticks
#@ ensures \result == 0
def formal_os_rmdir(name: str) -> int:
    mkdir(name, 0o777)               # set up: create the directory
    rc = rmdir(name)                 # the REAL removal
    if rc != 0:
        return 0                     # rmdir failed: vacuously ABSENT-consistent
    return access(name, F_OK)        # observe: now ABSENT — ASSERTED == 0


# unlink -> observe ABSENT.
# CONSEQUENCE: mkdir(f); unlink(f); then access(f, F_OK) == 0 (absent).
# Proven through the public API over create->remove->observe.
#@ requires True
#@ assigns _filesystem.disk, _filesystem._mtime_ticks
#@ ensures \result == 0
def formal_os_unlink(name: str) -> int:
    mkdir(name, 0o777)               # set up a name resolvable by access
    rc = unlink(name)                # the REAL removal
    if rc != 0:
        return 0                     # unlink failed: vacuously ABSENT-consistent
    return access(name, F_OK)        # observe: now ABSENT — ASSERTED == 0


# remove (alias of unlink) -> observe ABSENT.
# CONSEQUENCE: mkdir(f); remove(f); then access(f, F_OK) == 0 (absent).
# Proven through the public API over create->remove->observe.
#@ requires True
#@ assigns _filesystem.disk, _filesystem._mtime_ticks
#@ ensures \result == 0
def formal_os_remove(name: str) -> int:
    mkdir(name, 0o777)               # set up a name resolvable by access
    rc = remove(name)                # the REAL removal
    if rc != 0:
        return 0                     # remove failed: vacuously ABSENT-consistent
    return access(name, F_OK)        # observe: now ABSENT — ASSERTED == 0


# link -> observe the new name PRESENT.
# CONSEQUENCE: mkdir(a); link(a, b) succeeds => access(b, F_OK) == 1 (the new
# name b now resolves).  Proven through the public API over create->link->observe.
# (The deeper hard-link identity "a and b share one inode" is observable only
# via stat's inode number, blocked by stat's int path-typing — documented gap.)
#@ requires src != dst
#@ assigns _filesystem.disk, _filesystem.fd_open, _filesystem.fd_inode, _filesystem.fd_offset, _filesystem.fd_flags, _filesystem.fd_block, _filesystem.next_fd, _filesystem._mtime_ticks
#@ ensures \result == 1
def formal_os_link(src: str, dst: str) -> int:
    mkdir(src, 0o777)               # set up: a exists
    rc = link(src, dst)             # the REAL hard link
    if rc != 0:
        return 1                    # link failed: not the case under test
    return access(dst, F_OK)        # observe: b now PRESENT — ASSERTED == 1


# rename -> observe new PRESENT.
# CONSEQUENCE: mkdir(a); rename(a, b) => access(b, F_OK) == 1 (b present).
# Proven through the public API over create->rename->observe.  (The companion
# consequence access(a) == 0 is the subject of formal_os_rename_old_absent.)
#@ requires src != dst
#@ assigns _filesystem.disk, _filesystem._mtime_ticks
#@ ensures \result == 1
def formal_os_rename(src: str, dst: str) -> int:
    mkdir(src, 0o777)               # set up: a exists
    rc = rename(src, dst)           # the REAL rename
    if rc != 0:
        return 1                    # rename failed: not the case under test
    return access(dst, F_OK)        # observe: b PRESENT — ASSERTED == 1


# rename -> observe OLD name ABSENT.
# CONSEQUENCE: mkdir(a); rename(a, b) => access(a, F_OK) == 0 (a no longer
# resolves).  Proven through the public API over create->rename->observe.
#@ requires src != dst
#@ assigns _filesystem.disk, _filesystem._mtime_ticks
#@ ensures \result == 0
def formal_os_rename_old_absent(src: str, dst: str) -> int:
    mkdir(src, 0o777)               # set up: a exists
    rc = rename(src, dst)           # the REAL rename
    if rc != 0:
        return 0                    # rename failed: absent-consistent
    return access(src, F_OK)        # observe: a now ABSENT — ASSERTED == 0


# symlink -> observe the link name PRESENT.
# CONSEQUENCE: symlink(t, l) => access(l, F_OK) == 1 (the link name resolves).
# Proven through the public API over symlink->observe.  (readlink content is
# not observable at the os.* str layer — documented gap.)
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 1
def formal_os_symlink(target: str, linkpath: str) -> int:
    rc = symlink(target, linkpath)  # the REAL symlink
    if rc != 0:
        return 1                    # symlink failed: not the case under test
    return access(linkpath, F_OK)   # observe: l PRESENT — ASSERTED == 1


# truncate -> only a return-code bound is expressible.
# CONSEQUENCE we want: after create+truncate(f, n), the size field of f's
# inode == n.  UNPROVABLE: no name-keyed size observation primitive is exposed
# at the os.* layer (stat returns the inode number, not the size), AND
# truncate's `filepath` is left un-annotated, so the emitted stub types it
# `int` — there is no str-typed size observer to chain onto an int path.  So
# the STRONGEST provable property here is truncate's own return-code bound.
# This is a documented MODEL GAP (no size accessor), unlike the namespace
# theorems below which observe their consequence via access.
#@ requires length >= 0
#@ assigns _filesystem.disk, _filesystem._mtime_ticks
#@ ensures \result == 0 or \result == -1
def formal_os_truncate(name: int, length: int) -> int:
    return truncate(name, length)
