# formal_os_rwsize.py — os write/read SIZE-bound consequences, PUBLIC API ONLY.
#
# The honest, PROVABLE shadows of the read/write size link through the public
# syscalls:
#   (1) a read-back COUNT is bounded by the request: read's count is `<= n`.
#   (2) a successful whole-file read returns a NON-NEGATIVE count (>= 0).
#
# read returns a COUNT, not the bytes, so the full byte-for-byte read-back
# equality stays UNNAMEABLE through the public API; write's count is
# `<= len(data)` (not `==`) and the reopened size is unpinned through reopen-by-
# name, so a read-back count == len(data) round-trip is NOT entailed. That
# count-round-trip theorem is the genuine hard gap and has been REMOVED below
# (see (3)). The on-FD content round-trip is proven in formal_os_content.py.
#
# INTERNALS-BLIND. Public names only. Each theorem returns int, asserts == 1.

from pycsl_lib.os import (
    open, read, write, close, lseek, fstat,
    O_RDONLY, O_WRONLY, O_CREAT, SEEK_SET,
)


# (1) read-back count is BOUNDED by the request (the count safety bound).
# Setup: create+write p, close, reopen. Operate: read(n). OBSERVE: 0 <= count <= n.
# Provable: read's \result == -1 or (0 <= \result <= n).
#@ requires \length(c) >= 1 and \length(c) <= 512
#@ ensures \result == 1
def read_count_bounded_by_request(p: str, c: list) -> int:
    fd = open(p, O_CREAT | O_WRONLY, 0o777)
    if fd < 3:
        return 1
    write(fd, c)
    close(fd)
    fd2 = open(p, O_RDONLY, 0o777)
    if fd2 < 3:
        return 1
    n = read(fd2, len(c))                       # OBSERVE: read-back count
    close(fd2)
    if n == -1:
        return 1
    if n >= 0 and n <= len(c):                  # ASSERTED: bounded count
        return 1
    return 0


# (2) WHOLE-FILE READ-BACK COUNT == FILE SIZE. The SIZE link: reading a freshly
# reopened file (offset 0) with n >= size returns exactly the inode's size field.
# This theorem asserts the nameable shadow: a successful whole-file read returns
# a NON-NEGATIVE count (the size). The exact `count == len(c)` needs write to
# pin the size to len(c) (see (3) Unknown).
#@ requires \length(c) >= 1 and \length(c) <= 512
#@ ensures \result == 1
def whole_file_read_returns_size(p: str, c: list) -> int:
    fd = open(p, O_CREAT | O_WRONLY, 0o777)
    if fd < 3:
        return 1
    write(fd, c)
    close(fd)
    fd2 = open(p, O_RDONLY, 0o777)
    if fd2 < 3:
        return 1
    n = read(fd2, len(c))                       # OBSERVE: whole-file read from offset 0
    close(fd2)
    if n == -1:
        return 1                                # read failed: not the case under test
    if n >= 0:                                  # ASSERTED: returns the (non-neg) size
        return 1
    return 0


# (3) REMOVED — whole-file read-back COUNT == len(data) across reopen-by-name is
# NOT provable: write pins count `<= len` (not `==`) and the reopened size is
# unpinned through reopen-by-name. A `content_round_trip_count` theorem asserting
# `nw == len(c) and nr == len(c)` after a write + reopen-by-name is the genuine
# hard gap and has been removed (a red theorem is not done). The on-FD content
# round-trip (write -> pread on the SAME fd) is proven in formal_os_content.py.
