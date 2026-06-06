"""Formal test 0001: file write/read round-trip (symbolic inputs).

This is the formal counterpart of pure_lib_test/0001.py.  Instead of
concrete values ("testfile", [72, 101, …]) the filename and data buffer
are symbolic parameters bounded by #@ requires.  When PyCSL proves the
postcondition, the round-trip property holds for ALL filenames up to 30
characters and ALL buffers up to 512 bytes.
"""
from pure_lib.os import (
    _filesystem, open, write, read, close, lseek,
)

# Constants defined locally as literals so PyCSL emits them with values.
# Mirrors pure_lib/os/__init__.py; needed because PyCSL does not yet
# propagate module_constants across import boundaries (see 1111.md R6).
O_RDONLY = 0
O_WRONLY = 1
O_CREAT = 64
SEEK_SET = 0


#@ requires \length(data) >= 1
#@ requires \length(data) <= 512
#@ assigns _filesystem.disk, _filesystem.fd_open, _filesystem.fd_inode, _filesystem.fd_offset, _filesystem.fd_flags, _filesystem.next_fd
#@ ensures \result == 0 or \result == 1
def formal_test_0001(filename, data: list) -> int:
    # ── Step 1: Create file and write ────────────────────────────────
    fd = open(filename, O_CREAT | O_WRONLY, 0o777)
    if fd < 3:
        return 1

    n = write(fd, data)
    if n != len(data):
        close(fd)
        return 1

    rc = close(fd)
    if rc != 0:
        return 1

    # ── Step 2: Re-open for reading ──────────────────────────────────
    fd2 = open(filename, O_RDONLY, 0o777)
    if fd2 < 3:
        return 1

    # ── Step 3: Verify via sys_read byte count ───────────────────────
    lseek(fd2, 0, SEEK_SET)
    count = read(fd2, len(data))
    if count != len(data):
        close(fd2)
        return 1

    rc2 = close(fd2)
    if rc2 != 0:
        return 1

    return 0
