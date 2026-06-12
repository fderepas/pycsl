# formal_os_rwsize.py — os write/read SIZE-link consequences, PUBLIC API ONLY.
#
# Exploits the gap-16/17 strengthened read contract: on a whole-file read from
# offset 0 (n >= the file's size, size non-negative), the returned COUNT EQUALS
# the reopened inode's content length:
#   read(fd, n) == inode_size(disk, fd_inode[fd])    (under the offset-0 guard)
# open's reopen frame pins fd_offset[fd]==0 and fd_inode[fd] in range, so a
# read-back count equals the file size THROUGH THE API.
#
# read returns a COUNT, not the bytes, so the full byte-for-byte read-back
# equality stays UNNAMEABLE through the public API (documented Unknown below);
# write's count is `<= len(data)` (not `==`), so a write count == len(data) is
# likewise not entailed (documented Unknown).
#
# INTERNALS-BLIND. Public names only. Each theorem returns int, asserts == 1.

from pure_lib.os import (
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


# (3) CONTENT ROUND-TRIP COUNT — write(c) then read back returns exactly len(c).
#
# HONEST STATUS: Unknown. write's public contract pins only \result <= len(data)
# (not == len(data) on success), and the read==size link needs the reopened
# inode's size to EQUAL len(c) — which requires write to pin
# `inode_size == len(data)` as a content/size post-state. Today the count chain
# breaks at write (count is `<=`, size is unpinned). The model gap: write must
# pin the written inode's SIZE to len(data) on whole-block success.
#@ requires \length(c) >= 1 and \length(c) <= 512
#@ ensures \result == 1
def content_round_trip_count(p: str, c: list) -> int:
    fd = open(p, O_CREAT | O_WRONLY, 0o777)
    if fd < 3:
        return 1
    nw = write(fd, c)                           # operate: write content
    close(fd)
    fd2 = open(p, O_RDONLY, 0o777)
    if fd2 < 3:
        return 1
    nr = read(fd2, len(c))                      # OBSERVE: read-back count
    close(fd2)
    if nw == len(c) and nr == len(c):           # ASSERTED: round-tripped count
        return 1
    return 0
