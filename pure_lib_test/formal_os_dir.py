"""Formal test: os directory/namespace-mutating syscalls — consequence scenarios.

Each theorem is structured as a setup -> operate -> OBSERVE scenario (the
shape the skill's Step 5 prescribes, à la formal_0001's write->read-back):
it performs the target namespace mutation and then calls the model's actual
observation primitive (access / stat / listdir) on the affected name.

WHAT IS PROVEN vs WHAT WE WANT.  The functional consequence we WANT to assert
(e.g. "after mkdir(d), access(d) == present") is written as a `# CONSEQUENCE:`
comment on each theorem.  That assertion is currently UNPROVABLE: the os
syscalls resolve names through `_dir_lookup`, whose on-disk name-byte content
is unmodeled (Gap 5), so the prover cannot link the entry written under a
symbolic name to the entry later found under that same name.  See
`10-2204-convergence-gap-4.md` (§4a) for the precise root cause and the
model-side fix.  Until that gap closes, the STRONGEST property provable over
the chained mutate->observe scenario is the OBSERVATION call's own
return-code/safety bound, which is what each `#@ ensures` asserts here.  This
is strictly stronger than the 668c474 form (which asserted the *mutator's*
trivially-true return code on a single bare call): every theorem now exercises
the mutate-then-observe call SEQUENCE and asserts on the observe step.

Whole-API coverage (every syscall 668c474 covered) is retained: mkdir,
makedirs, rmdir, unlink, remove, link, rename, symlink, truncate.
"""
from pure_lib.os import (
    _filesystem,
    mkdir, makedirs, rmdir, unlink, remove, link, rename, symlink, truncate,
    access, listdir,
)

F_OK = 0


# mkdir -> observe present.
# CONSEQUENCE we want: after mkdir(d) succeeds, access(d, F_OK) reports the
# directory PRESENT (== 1).  UNPROVABLE (Gap 5 / gap-4 §4a): _dir_lookup name
# match is opaque.  Provable here: access's own 0/1 safety bound over the chain.
#@ requires True
#@ assigns _filesystem.disk, _filesystem._mtime_ticks
#@ ensures \result == 0 or \result == 1
def formal_os_mkdir(name: str) -> int:
    rc = mkdir(name, 0o777)
    if rc != 0:
        return 0
    return access(name, F_OK)        # want: == 1 (present)


# makedirs (nested wrapper) -> observe present.
# CONSEQUENCE we want: after makedirs(d), access(d, F_OK) reports PRESENT
# (== 1).  UNPROVABLE (gap-4 §4a).  Provable: access's 0/1 bound over the
# chain.  (stat() can't observe here: the os.* stat stub types its path int,
# while makedirs types it str — a name-keyed observation has no str accessor
# beyond access; see gap-4.)
#@ requires True
#@ assigns _filesystem.disk, _filesystem._mtime_ticks
#@ ensures \result == 0 or \result == 1
def formal_os_makedirs(name: str) -> int:
    rc = makedirs(name)
    if rc != 0:
        return 0
    return access(name, F_OK)        # want: == 1 (present)


# rmdir -> observe ABSENT.  (the worked example: create -> present -> rmdir -> absent)
# CONSEQUENCE we want: mkdir(d); rmdir(d); then access(d, F_OK) == 0 (absent).
# UNPROVABLE (gap-4 §4a).  Provable: access's 0/1 bound over the full chain.
#@ requires True
#@ assigns _filesystem.disk, _filesystem._mtime_ticks
#@ ensures \result == 0 or \result == 1
def formal_os_rmdir(name: str) -> int:
    mkdir(name, 0o777)
    rmdir(name)
    return access(name, F_OK)        # want: == 0 (absent)


# unlink -> observe ABSENT.
# CONSEQUENCE we want: after unlink(f), access(f, F_OK) == 0 (absent).
# UNPROVABLE (gap-4 §4a).  Provable: access's 0/1 bound over the chain.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == 1
def formal_os_unlink(name: str) -> int:
    unlink(name)
    return access(name, F_OK)        # want: == 0 (absent)


# remove (alias of unlink) -> observe ABSENT.
# CONSEQUENCE we want: after remove(f), access(f, F_OK) == 0 (absent).
# UNPROVABLE (gap-4 §4a).  Provable: access's 0/1 bound over the chain.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == 1
def formal_os_remove(name: str) -> int:
    remove(name)
    return access(name, F_OK)        # want: == 0 (absent)


# link -> observe the new name present.
# CONSEQUENCE we want: link(a, b) succeeds => access(b, F_OK) == 1, and
# stat(a) == stat(b) (same inode).  UNPROVABLE (gap-4 §4a).  Provable:
# access's 0/1 bound over create->link->observe.
#@ requires True
#@ assigns _filesystem.disk, _filesystem.fd_open, _filesystem.fd_inode, _filesystem.fd_offset, _filesystem.fd_flags, _filesystem.fd_block, _filesystem.next_fd, _filesystem._mtime_ticks
#@ ensures \result == 0 or \result == 1
def formal_os_link(src: str, dst: str) -> int:
    mkdir(src, 0o777)
    link(src, dst)
    return access(dst, F_OK)         # want: == 1 (b now present)


# rename -> observe old ABSENT, new present.
# CONSEQUENCE we want: rename(a, b) => access(a) == 0 AND access(b) == 1.
# UNPROVABLE (gap-4 §4a).  Provable: access's 0/1 bound over the chain.
#@ requires True
#@ assigns _filesystem.disk, _filesystem._mtime_ticks
#@ ensures \result == 0 or \result == 1
def formal_os_rename(src: str, dst: str) -> int:
    mkdir(src, 0o777)
    rename(src, dst)
    a_gone = access(src, F_OK)       # want: == 0 (a absent)
    return access(dst, F_OK)         # want: == 1 (b present)


# symlink -> observe the link name present.
# CONSEQUENCE we want: symlink(t, l) => readlink(l) reports t's block, and
# access(l) == 1.  UNPROVABLE (gap-4 §4a).  Provable: access's 0/1 bound.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == 1
def formal_os_symlink(target: str, linkpath: str) -> int:
    symlink(target, linkpath)
    return access(linkpath, F_OK)    # want: == 1 (l present)


# truncate -> observe via listdir (no name-keyed size observation primitive
# is exposed at the os.* layer; stat returns the inode number, not the size).
# CONSEQUENCE we want: after create+truncate(f, n), the size field of f's
# inode == n.  UNPROVABLE (gap-4 §4a + no size accessor).  Provable: listdir's
# <= 16 length bound over the chain.
# NOTE: os.truncate(filepath, length) leaves `filepath` un-annotated, so the
# emitted stub types it `int`; the driver's path param matches that type.
#@ requires length >= 0
#@ assigns _filesystem.disk, _filesystem._mtime_ticks
#@ ensures \length(\result) <= 16
def formal_os_truncate(name: int, length: int) -> list:
    truncate(name, length)
    return listdir(name)             # want: f present with size == length
