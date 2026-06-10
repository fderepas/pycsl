"""Formal test: os query / metadata syscalls — consequence scenarios.

These are the READ-ONLY observers (stat, lstat, fstat, readlink, access,
listdir, scandir, chmod, getcwd, getpid).  A consequence test for an observer
establishes a KNOWN object and then asserts the observer reports it correctly
(à la formal_0001: build state you control, observe it).

WHAT IS PROVEN vs WHAT WE WANT.  The functional consequence we WANT (e.g.
"after mkdir(d), stat(d) yields a valid inode for the dir we built") is
written as a `# CONSEQUENCE:` comment.  It is UNPROVABLE today: name-keyed
observation goes through `_dir_lookup`, whose on-disk name-byte content is
unmodeled (Gap 5), and a freshly-constructed filesystem has no contract pinning
its initial state (`__init__` has no `ensures`).  See
`10-2204-convergence-gap-4.md` (§4a, §4c).  The STRONGEST provable property
remains each observer's return-code/geometry bound (inode in [0,32), block in
[0,256), access 0/1, listdir length <= 16, getcwd/getpid constants), asserted
over a setup->observe scenario where the model's types permit chaining.

NOTE: os.stat/lstat/chmod/listdir/scandir leave their path param un-annotated,
so the emitted stub types it `int`; access/readlink type it `str`.  Where a
name-keyed setup (mkdir, str) cannot feed an int-typed observer, the observer
is exercised directly and the type mismatch is noted — itself a facet of the
gap (no str<->int-coherent name accessor).
"""
from pure_lib.os import (
    _filesystem,
    stat, lstat, fstat, readlink, access, listdir, scandir, chmod,
    getcwd, getpid, mkdir,
)

F_OK = 0


# stat: build a KNOWN dir, then stat it.
# CONSEQUENCE we want: mkdir(d) then stat(d) yields the dir's inode
# (0 <= ino < 32).  UNPROVABLE (gap-4 §4a) AND un-chainable by type (mkdir
# types path str, stat types it int).  Provable: stat's inode/-1 bound.
#@ requires True
#@ assigns \nothing
#@ ensures \result == -1 or (\result >= 0 and \result < 32)
def formal_os_stat(name: int) -> int:
    return stat(name)                # want: 0 <= ino < 32 for a built object


# lstat: like stat (no symlink follow in this model); same inode bound.
# CONSEQUENCE we want: lstat of a known object yields its inode.  UNPROVABLE.
#@ requires True
#@ assigns \nothing
#@ ensures \result == -1 or (\result >= 0 and \result < 32)
def formal_os_lstat(name: int) -> int:
    return lstat(name)               # want: 0 <= ino < 32 for a built object


# fstat: observe an open fd's inode.
# CONSEQUENCE we want: for an fd opened on a known file, fstat returns that
# file's inode.  UNPROVABLE (gap-4 §4b/§4c: open's ensures does not pin
# fd_inode; a fresh fs has no fd-table contract).  Provable: fstat's inode/-1.
#@ requires fd >= 0
#@ assigns \nothing
#@ ensures \result == -1 or (\result >= 0 and \result < 32)
def formal_os_fstat(fd: int) -> int:
    return fstat(fd)                 # want: the opened file's inode


# readlink: build a symlink, then read its target.
# CONSEQUENCE we want: symlink(t, l) then readlink(l) == t's stored block.
# UNPROVABLE (gap-4 §4a).  Provable: readlink's block/-1 bound over the chain.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == -1 or (\result >= 0 and \result < 256)
def formal_os_readlink(name: str) -> int:
    return readlink(name)            # want: the symlink target block


# access: created object -> True; never-created -> False.
# CONSEQUENCE we want: mkdir(d) => access(d) == 1; on a never-created name,
# access == 0.  UNPROVABLE (gap-4 §4a).  Provable: access's 0/1 bound over
# the create->observe chain.
#@ requires True
#@ assigns _filesystem.disk, _filesystem._mtime_ticks
#@ ensures \result == 0 or \result == 1
def formal_os_access(name: str, mode: int) -> int:
    mkdir(name, 0o777)
    return access(name, mode)        # want: == 1 (present after mkdir)


# chmod: set the mode, then (would) observe it.
# CONSEQUENCE we want: chmod(f, m) => stat(f)'s inode mode field == m.
# UNPROVABLE (gap-4 §4a + no mode accessor at the os.* layer).  Provable:
# chmod's own 0/-1 bound.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
def formal_os_chmod(name: int, mode: int) -> int:
    return chmod(name, mode)         # want: stat(name) mode reflects `mode`


# listdir: create N entries -> listdir count reflects them.
# CONSEQUENCE we want: after creating entries, len(listdir(d)) == N (or
# contains the names).  UNPROVABLE (gap-4 §4a).  Provable: listdir's <= 16
# length bound.
#@ requires True
#@ assigns \nothing
#@ ensures \length(\result) <= 16
def formal_os_listdir(name: int) -> list:
    return listdir(name)             # want: count == number of entries built


# scandir: same as listdir; length <= 16.
# CONSEQUENCE we want: scandir count reflects the entries built.  UNPROVABLE.
#@ requires True
#@ assigns \nothing
#@ ensures \length(\result) <= 16
def formal_os_scandir(name: int) -> list:
    return scandir(name)             # want: count == number of entries built


# getcwd: chdir(d) -> getcwd() == d.  No chdir in this model; getcwd is the
# CONSTANT root inode (0).  Honestly: this asserts the modeled constant, not a
# chdir consequence (the model exposes no chdir to round-trip against).
#@ requires True
#@ assigns \nothing
#@ ensures \result == 0
def formal_os_getcwd() -> int:
    return getcwd()                  # constant: root inode 0 (no chdir to observe)


# getpid: CONSTANT (the modeled pid, 1).  No mutating consequence to
# round-trip; this honestly asserts the constant, not a functional effect.
#@ requires True
#@ assigns \nothing
#@ ensures \result == 1
def formal_os_getpid() -> int:
    return getpid()                  # constant: pid 1 (no consequence)
