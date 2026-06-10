"""Formal test: os directory-mutating syscalls (symbolic inputs).

Propagates the source-of-truth return-code disjunction each directory
syscall guarantees, over SYMBOLIC path arguments.  Where formal_0001 /
formal_0008 cover the open->write->close->reopen->read I/O path, this file
closes the loop over the *namespace-mutating* calls: mkdir, rmdir,
unlink/remove, link, rename, symlink, truncate.

Each theorem constructs (reuses) the global filesystem and drives one
syscall on a symbolic path, asserting the literal return-code disjunction
its proven `#@ ensures` guarantees.  Valid here = the promise holds for
EVERY path argument in range.
"""
from pure_lib.os import (
    _filesystem,
    mkdir, makedirs, rmdir, unlink, remove, link, rename, symlink, truncate,
)


# mkdir: POSIX mkdir() returns 0 on success, -1 on EEXIST/ENFILE/ENOSPC.
# cite: pure_lib/os/__init__.py mkdir  -> `#@ ensures \result == 0 or \result == -1`
# cite: UnixInodeFileSystem.sys_mkdir  -> `#@ ensures \result == 0 or \result == -1`
#@ requires True
#@ assigns _filesystem.disk, _filesystem._mtime_ticks
#@ ensures \result == 0 or \result == -1
def formal_os_mkdir(name: str) -> int:
    return mkdir(name, 0o777)


# makedirs: wrapper over sys_mkdir (single level here); same 0/-1 promise.
# cite: pure_lib/os/__init__.py makedirs -> `#@ ensures \result == 0 or \result == -1`
#@ requires True
#@ assigns _filesystem.disk, _filesystem._mtime_ticks
#@ ensures \result == 0 or \result == -1
def formal_os_makedirs(name: str) -> int:
    return makedirs(name)


# rmdir: POSIX rmdir() returns 0, or -1 on ENOENT/ENOTDIR.
# cite: pure_lib/os/__init__.py rmdir   -> `#@ ensures \result == 0 or \result == -1`
# cite: UnixInodeFileSystem.sys_rmdir   -> `#@ ensures \result == 0 or \result == -1`
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
def formal_os_rmdir(name: str) -> int:
    return rmdir(name)


# unlink: POSIX unlink() returns 0, or -1 on ENOENT.
# cite: pure_lib/os/__init__.py unlink  -> `#@ ensures \result == 0 or \result == -1`
# cite: UnixInodeFileSystem.sys_unlink  -> `#@ ensures \result == 0 or \result == -1`
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
def formal_os_unlink(name: str) -> int:
    return unlink(name)


# remove: alias of unlink; same 0/-1 promise.
# cite: pure_lib/os/__init__.py remove  -> `#@ ensures \result == 0 or \result == -1`
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
def formal_os_remove(name: str) -> int:
    return remove(name)


# link: POSIX link() returns 0, or -1 on ENOENT / full root dir.
# cite: pure_lib/os/__init__.py link    -> `#@ ensures \result == 0 or \result == -1`
# cite: UnixInodeFileSystem.sys_link    -> `#@ ensures \result == 0 or \result == -1`
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
def formal_os_link(src: str, dst: str) -> int:
    return link(src, dst)


# rename: POSIX rename() returns 0, or -1 on ENOENT / full dir.
# cite: pure_lib/os/__init__.py rename  -> `#@ ensures \result == 0 or \result == -1`
# cite: UnixInodeFileSystem.sys_rename  -> `#@ ensures \result == 0 or \result == -1`
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
def formal_os_rename(src: str, dst: str) -> int:
    return rename(src, dst)


# symlink: POSIX symlink() returns 0, or -1 on EEXIST / alloc failure.
# cite: pure_lib/os/__init__.py symlink -> `#@ ensures \result == 0 or \result == -1`
# cite: UnixInodeFileSystem.sys_symlink -> `#@ ensures \result == 0 or \result == -1`
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
def formal_os_symlink(target: str, linkpath: str) -> int:
    return symlink(target, linkpath)


# truncate: POSIX truncate() returns 0, or -1 on ENOENT / bad length.
# cite: pure_lib/os/__init__.py truncate -> `#@ ensures \result == 0 or \result == -1`
# cite: UnixInodeFileSystem.sys_truncate -> `#@ ensures \result == 0 or \result == -1`
# NOTE: os.truncate(filepath, length) leaves `filepath` un-annotated, so the
# emitted stub types it `int`; the driver's path param matches that type.
#@ requires length >= 0
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
def formal_os_truncate(name: int, length: int) -> int:
    return truncate(name, length)
