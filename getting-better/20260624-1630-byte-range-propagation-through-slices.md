# 20260624-1630-byte-range-propagation-through-slices.md

**Date:** 2026-06-24
**Type:** Ergonomics gap (PyCSL feature request)
**Status:** PROPOSED

## Problem

When a function reads a slice `entry_bytes = self.disk[off : off + 32]` and
passes it to a callee that requires byte-range facts (`0 <= data[0] <= 255`),
the byte-range facts from class invariants (e.g. `inode_bytes_valid(self.disk)`)
do **not propagate through the array slice**. The caller cannot discharge the
callee's byte-range preconditions.

Concretely: `_unpack_direntry(data)` calls `_unpack_uint16_be(data, 0)` which
requires `0 <= data[0] <= 255` and `0 <= data[1] <= 255`. The caller
(`_read_directory` / `listdir` / `scandir`) reads
`entry_bytes = self.disk[off : off + 32]` and passes it. The class invariant
`inode_bytes_valid(self.disk)` gives `forall i. 512 <= i < 2560 -> 0 <= d[i] <= 255`
— but (a) the directory region [2560, 3072) is outside this range, and (b) even
within range, the fact `0 <= self.disk[off] <= 255` does not transfer to
`0 <= entry_bytes[0] <= 255` because PyCSL's slice-read handler does not emit
`entry_bytes[k] == self.disk[off + k]` as a postcondition.

## Proposed feature

1. **Slice-read postconditions:** When `b = a[lo:hi]` is read, emit
   `ensures forall k. 0 <= k < (hi - lo) -> b[k] == a[lo + k]` (definitional,
   zero TCB — analogous to the A1 slice-write assert). This lets callers
   transfer byte-range facts from the source array to the slice.

2. **Byte-range invariant for directory regions:** Either extend
   `inode_bytes_valid` to cover the directory block range, or add a separate
   `dir_bytes_valid` class invariant maintained by the directory mutators
   (which already write byte-valued entries via `_build_direntry`).

## Impact

Would close GAP A2 (`_unpack_direntry` 2 Unknown) and unblock body-verification
of any function that reads directory entries from `self.disk`.
