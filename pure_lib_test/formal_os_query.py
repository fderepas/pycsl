"""Formal test: os query / metadata syscalls (symbolic inputs).

Propagates the source-of-truth bounds each read-only metadata syscall
guarantees, over SYMBOLIC arguments.  These calls do not mutate the
filesystem (`assigns \\nothing`) and return either a sentinel -1 or a
value bounded by the filesystem geometry (inode numbers in [0,32),
block numbers in [0,256)).

Covered: stat, lstat, fstat, readlink, access, listdir, scandir, chmod,
getcwd, getpid.
"""
from pure_lib.os import (
    _filesystem,
    stat, lstat, fstat, readlink, access, listdir, scandir, chmod,
    getcwd, getpid,
)


# stat: returns inode number in [0,32), or -1 on ENOENT.
# cite: pure_lib/os/__init__.py stat    -> `#@ ensures \result == -1 or (\result >= 0 and \result < 32)`
# cite: UnixInodeFileSystem.sys_stat    -> `#@ ensures \result == -1 or (\result >= 0 and \result < 32)`
# NOTE: os.stat/lstat/chmod/listdir/scandir leave their path param
# un-annotated, so the emitted stub types it `int`; the driver matches.
#@ requires True
#@ assigns \nothing
#@ ensures \result == -1 or (\result >= 0 and \result < 32)
def formal_os_stat(name: int) -> int:
    return stat(name)


# lstat: like stat (no symlink follow in this model); same inode bound.
# cite: pure_lib/os/__init__.py lstat   -> `#@ ensures \result == -1 or (\result >= 0 and \result < 32)`
#@ requires True
#@ assigns \nothing
#@ ensures \result == -1 or (\result >= 0 and \result < 32)
def formal_os_lstat(name: int) -> int:
    return lstat(name)


# fstat: returns inode number in [0,32) for an open fd, or -1 on EBADF.
# cite: pure_lib/os/__init__.py fstat   -> `#@ ensures \result == -1 or (\result >= 0 and \result < 32)`
# cite: UnixInodeFileSystem.sys_fstat   -> `#@ ensures \result == -1 or (\result >= 0 and \result < 32)`
#@ requires fd >= 0
#@ assigns \nothing
#@ ensures \result == -1 or (\result >= 0 and \result < 32)
def formal_os_fstat(fd: int) -> int:
    return fstat(fd)


# readlink: returns the symlink target block in [0,256), or -1.
# cite: pure_lib/os/__init__.py readlink -> `#@ ensures \result == -1 or (\result >= 0 and \result < 256)`
# cite: UnixInodeFileSystem.sys_readlink -> `#@ ensures \result == -1 or (\result >= 0 and \result < 256)`
#@ requires True
#@ assigns \nothing
#@ ensures \result == -1 or (\result >= 0 and \result < 256)
def formal_os_readlink(name: str) -> int:
    return readlink(name)


# access: returns 1 if accessible, 0 otherwise (os wrapper maps sys_access).
# cite: pure_lib/os/__init__.py access  -> `#@ ensures \result == 0 or \result == 1`
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == 1
def formal_os_access(name: str, mode: int) -> int:
    return access(name, mode)


# chmod: returns 0 on success, -1 on ENOENT.
# cite: pure_lib/os/__init__.py chmod   -> `#@ ensures \result == 0 or \result == -1`
# cite: UnixInodeFileSystem.sys_chmod   -> `#@ ensures \result == 0 or \result == -1`
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
def formal_os_chmod(name: int, mode: int) -> int:
    return chmod(name, mode)


# listdir: returns a list of entry names with length <= 16 (a directory
# block holds 16 fixed-width entries; return-arr.md).
# cite: pure_lib/os/__init__.py listdir -> `#@ ensures \length(\result) <= 16`
#@ requires True
#@ assigns \nothing
#@ ensures \length(\result) <= 16
def formal_os_listdir(name: int) -> list:
    return listdir(name)


# scandir: returns a list of inode numbers, length <= 16.
# cite: pure_lib/os/__init__.py scandir -> `#@ ensures \length(\result) <= 16`
#@ requires True
#@ assigns \nothing
#@ ensures \length(\result) <= 16
def formal_os_scandir(name: int) -> list:
    return scandir(name)


# getcwd: returns the root inode (0) in this model.
# cite: pure_lib/os/__init__.py getcwd  -> `#@ ensures \result == 0`
#@ requires True
#@ assigns \nothing
#@ ensures \result == 0
def formal_os_getcwd() -> int:
    return getcwd()


# getpid: returns the simulated pid (1).
# cite: pure_lib/os/__init__.py getpid  -> `#@ ensures \result == 1`
#@ requires True
#@ assigns \nothing
#@ ensures \result == 1
def formal_os_getpid() -> int:
    return getpid()
