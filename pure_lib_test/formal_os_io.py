"""Formal test: os I/O / fd syscalls not covered by formal_0001/0008.

formal_0001 (byte-count round-trip) and formal_0008 (content round-trip)
drive open/write/read/close/lseek through the global `_filesystem`.  This
file closes the loop over the remaining syscall surface:

  * dup           — the one fd syscall with a module-level os.* wrapper.
  * dup2, getdents, fsync, ftruncate, creat, chown, utimensat — syscalls
    with NO module-level os.* wrapper.

The wrapper-less syscalls are reached as instance methods.  PyCSL DOES
propagate an instance method's `#@ ensures` to the caller WHEN the instance
is constructed locally in the driver (the os filesystem is a fielded class,
so `UnixInodeFileSystem()` constructs cleanly).  Each theorem therefore
builds a fresh filesystem and re-states the syscall's proven return-code
disjunction over SYMBOLIC fd / path-as-int / value inputs.
"""
from pure_lib.os import _filesystem, dup
from pure_lib.os.UnixInodeFileSystem import UnixInodeFileSystem


# dup: POSIX dup() returns a new fd (>= 3) or -1 on EBADF / full table.
# Propagated via the module-level os.dup wrapper.
# cite: pure_lib/os/__init__.py dup     -> `#@ ensures \result == -1 or \result >= 3`
# cite: UnixInodeFileSystem.sys_dup     -> `#@ ensures \result == -1 or \result >= 3`
#@ requires fd >= 0
#@ assigns _filesystem.fd_open, _filesystem.fd_inode, _filesystem.fd_offset, _filesystem.fd_flags, _filesystem.next_fd
#@ ensures \result == -1 or \result >= 3
def formal_os_dup(fd: int) -> int:
    return dup(fd)


# dup2: POSIX dup2() returns the requested newfd, or -1 on EBADF.
# cite: UnixInodeFileSystem.sys_dup2    -> `#@ ensures \result == newfd or \result == -1`
#@ requires oldfd >= 0
#@ requires newfd >= 0
#@ ensures \result == newfd or \result == -1
def formal_os_dup2(oldfd: int, newfd: int) -> int:
    fs = UnixInodeFileSystem()
    return fs.sys_dup2(oldfd, newfd)


# getdents: Linux getdents() returns 0, or -1 on EBADF / ENOTDIR.
# cite: UnixInodeFileSystem.sys_getdents -> `#@ ensures \result == 0 or \result == -1`
#@ requires fd >= 0
#@ ensures \result == 0 or \result == -1
def formal_os_getdents(fd: int) -> int:
    fs = UnixInodeFileSystem()
    return fs.sys_getdents(fd)


# fsync: POSIX fsync() returns 0 when fd valid, else -1 on EBADF.
# cite: UnixInodeFileSystem.sys_fsync   -> `#@ ensures \result == 0 or \result == -1`
#@ requires fd >= 0
#@ ensures \result == 0 or \result == -1
def formal_os_fsync(fd: int) -> int:
    fs = UnixInodeFileSystem()
    return fs.sys_fsync(fd)


# ftruncate: POSIX ftruncate() returns 0, or -1 on EBADF / bad length.
# cite: UnixInodeFileSystem.sys_ftruncate -> `#@ ensures \result == 0 or \result == -1`
#@ requires fd >= 0
#@ ensures \result == 0 or \result == -1
def formal_os_ftruncate(fd: int, length: int) -> int:
    fs = UnixInodeFileSystem()
    return fs.sys_ftruncate(fd, length)


# creat: POSIX creat() returns a new fd (>= 3) or -1 on alloc/dir-full.
# cite: UnixInodeFileSystem.sys_creat   -> `#@ ensures \result == -1 or \result >= 3`
#@ requires True
#@ ensures \result == -1 or \result >= 3
def formal_os_creat(name: str, mode: int) -> int:
    fs = UnixInodeFileSystem()
    return fs.sys_creat(name, mode)


# chown: POSIX chown() returns 0, or -1 on ENOENT.
# cite: UnixInodeFileSystem.sys_chown   -> `#@ ensures \result == 0 or \result == -1`
#@ requires True
#@ ensures \result == 0 or \result == -1
def formal_os_chown(name: str, owner: int, group: int) -> int:
    fs = UnixInodeFileSystem()
    return fs.sys_chown(name, owner, group)


# utimensat: Linux utimensat() returns 0, or -1 on ENOENT.
# cite: UnixInodeFileSystem.sys_utimensat -> `#@ ensures \result == 0 or \result == -1`
#@ requires True
#@ ensures \result == 0 or \result == -1
def formal_os_utimensat(name: str, atime: int, mtime: int) -> int:
    fs = UnixInodeFileSystem()
    return fs.sys_utimensat(name, atime, mtime)
