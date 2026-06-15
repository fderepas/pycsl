"""Formal test: file CONTENT round-trip through the public os API (gap-17).

Given a valid open descriptor at offset 0, the bytes written are EXACTLY the bytes read
back: write(fd, c) then pread(fd, len(c), 0) returns c. The content `c` is symbolic, so
`\\result == True` holds for ALL content in range. The equality is the load-bearing
ASSERT (`\\array_eq(back, c)`), proven by composing write's and pread's folded
`block_content_eq` atoms — the gap-17 content effect through the public API.

This standalone test is unblocked by the test-harness fixes: bool-return encoding
(`\\result == True`), trailing-assert-in-`if` emission, and slot_inode decl for importer
tests (the os type invariant).
"""
from pure_lib.os import _filesystem, write, pread


#@ requires fd >= 3 and fd < 64
#@ requires _filesystem.fd_open[fd] == 1
#@ requires 0 <= _filesystem.fd_inode[fd] and _filesystem.fd_inode[fd] < 32
#@ requires _filesystem.fd_offset[fd] == 0
#@ requires \length(c) >= 1 and \length(c) <= 512
#@ assigns _filesystem.disk, _filesystem.fd_offset, _filesystem.fd_block, _filesystem._mtime_ticks
#@ ensures \result == True
def formal_test_0009(fd: int, c: list) -> bool:
    w = write(fd, c)
    if w == len(c):
        back = pread(fd, len(c), 0)
        #@ assert \array_eq(back, c)
    return True
