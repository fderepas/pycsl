"""Formal test: os I/O / fd syscalls — consequence scenarios.

formal_0001 drives the open->write->read->close byte-COUNT round-trip through
the global `_filesystem`.  This file covers the remaining fd-syscall surface:
dup (module-level wrapper) and dup2, getdents, fsync, ftruncate, creat, chown,
utimensat (reached as instance methods on a locally-constructed filesystem,
whose `#@ ensures` then propagate to the caller).

WHAT IS PROVEN vs WHAT WE WANT.  The functional consequence we WANT (e.g.
"dup(fd) -> reading via the new fd sees the SAME data"; "creat(f) -> fstat(fd)
reports a valid file inode") is written as a `# CONSEQUENCE:` comment.  It is
UNPROVABLE today: the fd-mutating syscalls' contracts pin ONLY the return code,
never the resulting fd-table columns or disk bytes (`sys_creat`/`sys_open` are
`#@ no_inline` with a return-code-only `ensures`; `sys_read` bounds the byte
COUNT, not the bytes; `__init__` has no `ensures`).  So an observation call
reads an unconstrained post-state.  See `10-2204-convergence-gap-4.md`
(§4b, §4c).  The STRONGEST provable property over each chained scenario is the
observation/operation call's own return-code/safety bound, asserted here.
"""
from pure_lib.os import _filesystem, dup
from pure_lib.os.UnixInodeFileSystem import UnixInodeFileSystem


# dup -> read via the new fd.
# CONSEQUENCE we want: dup(fd) yields nd; reading via nd sees the SAME bytes
# the original fd's file holds.  UNPROVABLE (gap-4 §4b: dup's ensures pins only
# \result >= 3; read bounds only the byte count).  Provable: dup's >=3/-1 bound.
#@ requires fd >= 0
#@ assigns _filesystem.fd_open, _filesystem.fd_inode, _filesystem.fd_offset, _filesystem.fd_flags, _filesystem.next_fd
#@ ensures \result == -1 or \result >= 3
def formal_os_dup(fd: int) -> int:
    return dup(fd)                   # want: read(nd) sees the same data as fd


# dup2 -> observe the alias.
# CONSEQUENCE we want: dup2(oldfd, newfd) makes newfd alias oldfd (fstat(newfd)
# == fstat(oldfd)).  UNPROVABLE (gap-4 §4b/§4c: dup2 pins only the return fd;
# a fresh fs has no fd-table contract).  Provable: dup2's newfd/-1 bound.
#@ requires oldfd >= 0
#@ requires newfd >= 0
#@ ensures \result == newfd or \result == -1
def formal_os_dup2(oldfd: int, newfd: int) -> int:
    fs = UnixInodeFileSystem()
    rc = fs.sys_dup2(oldfd, newfd)
    # want: fs.sys_fstat(newfd) == fs.sys_fstat(oldfd) (alias established)
    return rc


# getdents -> observe directory entries.
# CONSEQUENCE we want: for an fd on a directory, getdents succeeds (0) and the
# entries match listdir.  UNPROVABLE (gap-4 §4b/§4c).  Provable: getdents 0/-1.
#@ requires fd >= 0
#@ ensures \result == 0 or \result == -1
def formal_os_getdents(fd: int) -> int:
    fs = UnixInodeFileSystem()
    return fs.sys_getdents(fd)       # want: 0 and entries == listdir


# fsync -> durability: read-back STILL equal after flush.
# CONSEQUENCE we want: after write+fsync, a read-back is UNCHANGED (fsync is a
# flush, not a mutation).  This is a flush with no functional effect to round-
# trip; honestly, fsync asserts only validity (0 when fd valid, else -1).
#@ requires fd >= 0
#@ ensures \result == 0 or \result == -1
def formal_os_fsync(fd: int) -> int:
    fs = UnixInodeFileSystem()
    return fs.sys_fsync(fd)          # flush: read-back stays equal (durability)


# ftruncate -> observe the new size.
# CONSEQUENCE we want: ftruncate(fd, n) => the file's inode size field == n
# (via fstat/stat).  UNPROVABLE (gap-4 §4b: ftruncate pins only 0/-1; no size
# accessor links to the fd's inode here).  Provable: ftruncate's 0/-1 bound.
#@ requires fd >= 0
#@ ensures \result == 0 or \result == -1
def formal_os_ftruncate(fd: int, length: int) -> int:
    fs = UnixInodeFileSystem()
    return fs.sys_ftruncate(fd, length)   # want: stat(file).size == length


# creat -> observe the new file present + a valid fd.
# CONSEQUENCE we want: creat(f) => f PRESENT and fstat(fd) reports a valid file
# inode (0 <= ino < 32).  UNPROVABLE (gap-4 §4a name-keyed + §4b creat pins
# only \result >= 3, not fd_inode).  Provable: creat's >=3/-1 bound.
#@ requires True
#@ ensures \result == -1 or \result >= 3
def formal_os_creat(name: str, mode: int) -> int:
    fs = UnixInodeFileSystem()
    fd = fs.sys_creat(name, mode)
    # want: fs.sys_fstat(fd) in [0,32) and access(name) present
    return fd


# chown -> observe owner/group.
# CONSEQUENCE we want: chown(f, u, g) => stat(f)'s uid/gid fields == u/g.
# UNPROVABLE (gap-4 §4a + no owner accessor).  Provable: chown's 0/-1 bound.
#@ requires True
#@ ensures \result == 0 or \result == -1
def formal_os_chown(name: str, owner: int, group: int) -> int:
    fs = UnixInodeFileSystem()
    return fs.sys_chown(name, owner, group)   # want: stat owner/group == u/g


# utimensat -> observe times.
# CONSEQUENCE we want: utimensat(f, a, m) => stat(f)'s atime/mtime == a/m.
# UNPROVABLE (gap-4 §4a + no time accessor).  Provable: utimensat's 0/-1 bound.
#@ requires True
#@ ensures \result == 0 or \result == -1
def formal_os_utimensat(name: str, atime: int, mtime: int) -> int:
    fs = UnixInodeFileSystem()
    return fs.sys_utimensat(name, atime, mtime)   # want: stat times == a/m
