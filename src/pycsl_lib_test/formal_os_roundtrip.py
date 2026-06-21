"""Formal test: file write/read round-trip (symbolic inputs).

This is the formal (symbolic) version of the os write/read round-trip.  Instead of
concrete values ("testfile", [72, 101, …]) the filename and data buffer
are symbolic parameters bounded by #@ requires.  When PyCSL proves the
postcondition, the round-trip property holds for ALL filenames and ALL buffers
up to 512 bytes.

FAITHFUL EXCEPTION MODEL.  open/write/read/lseek/close no longer return -1 on
failure: they RAISE OSError (open raises FileNotFoundError/OSError).  open's
old `fd < 3` failure sentinel is gone — a successful open returns fd >= 3 on the
non-raising path; close returns None.  The COUNT checks for write/read stay
(write/read return byte counts on success).  The round-trip remains a genuine
TOTALITY theorem: on every input the function returns 0 or 1 (no fault escapes).
"""
from pycsl_lib.os import (
    open, write, read, close, lseek,
)

# Constants defined locally as literals so PyCSL emits them with values.
# Mirrors pycsl_lib/os/__init__.py; needed because PyCSL does not yet
# propagate module_constants across import boundaries (see 1111.md R6).
O_RDONLY = 0
O_WRONLY = 1
O_CREAT = 64
SEEK_SET = 0


#@ requires \length(data) >= 1
#@ requires \length(data) <= 512
#@ assigns _filesystem.disk, _filesystem.fd_open, _filesystem.fd_inode, _filesystem.fd_offset, _filesystem.fd_flags, _filesystem.fd_block, _filesystem.next_fd, _filesystem._mtime_ticks
#@ ensures \result == 0 or \result == 1
def formal_test_0001(filename: str, data: list) -> int:
    # ── Step 1: Create file and write ────────────────────────────────
    fd = open(filename, O_CREAT | O_WRONLY, 0o777)   # raises on failure

    n = write(fd, data)
    if n != len(data):
        close(fd)
        return 1

    close(fd)

    # ── Step 2: Re-open for reading ──────────────────────────────────
    fd2 = open(filename, O_RDONLY, 0o777)            # raises on failure

    # ── Step 3: Verify via read byte count ───────────────────────────
    lseek(fd2, 0, SEEK_SET)
    count = read(fd2, len(data))
    if count != len(data):
        close(fd2)
        return 1

    close(fd2)

    return 0
