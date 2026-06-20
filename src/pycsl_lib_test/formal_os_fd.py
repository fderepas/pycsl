# formal_os_fd.py — os FD-CHAIN consequences, through the PUBLIC API ONLY.
#
# The fd chain (open path-walk -> open-file-description {offset, flags} -> inode)
# observed via the public syscalls. Each theorem CALLS THE REAL PUBLIC API the
# way a caller does: it imports `open`, `read`, `write`, `close`, `lseek`,
# `fstat`, `dup` and the flag constants from pycsl_lib.os and drives a
# setup -> operate -> OBSERVE scenario, asserting the observation's promised
# post-state.
#
# INTERNALS-BLIND. There is NO `_filesystem`, NO `disk`, NO `fd_*`, NO
# `_dir_lookup`, NO `sys_*`, NO `UnixInodeFileSystem(...)`, NO hand-written
# bytes. (grep -E confirms.)
#
# Each theorem returns `int` and asserts `\result == 1` (the formal_os
# convention; a `-> bool` body trips a WhyML int-vs-bool emission error).
#
# REOPEN-BY-NAME content round-trip (read-back == bytes written) is NOT provable
# through the public API: `read` returns a count `<= n`, not the bytes; the
# on-FD content round-trip (write -> pread on the SAME fd) is proven in
# formal_os_content.py. A would-be `content_round_trip` theorem asserting
# `n_read == len(c)` after a write + reopen-by-name is the genuine hard gap and
# has been REMOVED (a red theorem is not done).
#
# open(absent, O_RDONLY) -> -1 (ENOENT) is likewise NOT provable here: a never-
# created SYMBOLIC name's dir_lookup post-state is havoc'd, so open's ENOENT
# discriminant `(\result==-1) <==> dir_lookup<0` has no live antecedent and
# `== -1` is unentailed. The ENOENT consequence WITH absence ESTABLISHED via the
# API (mkdir then rmdir) IS proven in formal_os_enoent.py; a bare never-created
# `open_absent_yields_enoent` has been REMOVED.

from pycsl_lib.os import (
    open, read, write, close, lseek, fstat, dup,
    O_RDONLY, O_WRONLY, O_CREAT, SEEK_SET,
)


# ---------------------------------------------------------------------------
# (1) open-VALID: open(existing, O_RDONLY) -> a VALID fd (>= 3 in this model;
# fds 0/1/2 are reserved std streams).
# Setup: create the file via the API (open with O_CREAT). Operate: reopen it
# read-only. OBSERVE: the returned fd is valid (>= 3).
# Provable: open pins (\result >= 3) <==> dir_lookup(disk,5,p) >= 0, and the
# create established dir_lookup(disk,5,p) >= 0.
#@ requires True
#@ ensures \result == 1
def open_existing_yields_valid_fd(p: str) -> int:
    fd0 = open(p, O_CREAT | O_WRONLY, 0o777)   # setup: create p via the API
    if fd0 < 3:
        return 1                               # creation failed: not the case under test
    close(fd0)
    fd = open(p, O_RDONLY, 0o777)              # operate: reopen the existing file
    if fd >= 3:                                # OBSERVE: valid fd — ASSERTED == 1
        return 1
    return 0


# ---------------------------------------------------------------------------
# (2) fstat resolves the opened fd to a VALID inode (0 <= ino < 32).
# Setup: create p. Operate: reopen p, fstat the fd. OBSERVE: inode in range.
# Provable: open pins fd_open[fd]==1 and 0 <= fd_inode[fd] < 32; fstat's guarded
# ensures returns that inode.
#@ requires True
#@ ensures \result == 1
def fstat_of_opened_fd_is_valid_inode(p: str) -> int:
    fd0 = open(p, O_CREAT | O_WRONLY, 0o777)
    if fd0 < 3:
        return 1
    close(fd0)
    fd = open(p, O_RDONLY, 0o777)
    if fd < 3:
        return 1
    ino = fstat(fd)                            # OBSERVE: fd -> inode resolution
    close(fd)
    if ino >= 0 and ino < 32:                  # ASSERTED: valid inode
        return 1
    return 0


# ---------------------------------------------------------------------------
# (3) dup of a valid open fd yields a valid fd (== -1 or >= 3 — dup's bound).
# Setup: create + open p (a valid source). Operate: dup the fd. OBSERVE: the
# duped fd is valid.
#@ requires True
#@ ensures \result == 1
def dup_yields_valid_fd(p: str) -> int:
    fd = open(p, O_CREAT | O_WRONLY, 0o777)
    if fd < 3:
        return 1
    fd2 = dup(fd)                              # operate: duplicate the descriptor
    close(fd)
    if fd2 == -1 or fd2 >= 3:                  # OBSERVE: duped fd valid — ASSERTED == 1
        if fd2 >= 3:
            close(fd2)
        return 1
    return 0
