"""Test 0001: file write/read round-trip via pure_lib/os.

Scenario:
  1. Create a file and write a known string.
  2. Close the file.
  3. Re-open the file for reading.
  4. Read the data and verify it matches the original string.

The virtual filesystem stores data on disk blocks. After sys_write the bytes
live in _filesystem.disk, and we recover them by locating the file's inode
and reading from its data block.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pure_lib.os import (
    _filesystem, open, write, read, close, stat, fstat, lseek,
    O_CREAT, O_WRONLY, O_RDONLY, SEEK_SET,
)

TEST_STRING = "Hello, PyCSL filesystem!"
TEST_BYTES = [ord(c) for c in TEST_STRING]

# ── Step 1: Create file and write ────────────────────────────────────
fd = open("testfile", O_CREAT | O_WRONLY)
assert fd >= 3, f"open failed: fd={fd}"

n = write(fd, TEST_BYTES)
assert n == len(TEST_BYTES), f"write returned {n}, expected {len(TEST_BYTES)}"

rc = close(fd)
assert rc == 0, f"close failed: rc={rc}"

# ── Step 2: Re-open for reading ──────────────────────────────────────
fd2 = open("testfile", O_RDONLY)
assert fd2 >= 3, f"re-open failed: fd2={fd2}"

# ── Step 3: Read back and verify ─────────────────────────────────────
# sys_read returns byte count; actual bytes are on _filesystem.disk.
# Locate the file's data block via its inode.
ino = fstat(fd2)
assert ino >= 0, f"fstat failed: ino={ino}"

inode = _filesystem._read_inode(ino)
data_block = inode[8]
assert data_block > 0, f"no data block allocated: block={data_block}"

# Read from the raw disk at the data block offset
disk_offset = data_block * 512
read_back = _filesystem.disk[disk_offset:disk_offset + len(TEST_BYTES)]
recovered = ''.join(chr(b) for b in read_back)

assert recovered == TEST_STRING, (
    f"round-trip mismatch:\n"
    f"  wrote:  {TEST_STRING!r}\n"
    f"  read:   {recovered!r}"
)

# Also verify sys_read returns the correct byte count
lseek(fd2, 0, SEEK_SET)
count = read(fd2, len(TEST_BYTES))
assert count == len(TEST_BYTES), f"read count {count} != {len(TEST_BYTES)}"

rc2 = close(fd2)
assert rc2 == 0, f"close failed: rc2={rc2}"

print("PASS: 0001 — file write/read round-trip OK")
