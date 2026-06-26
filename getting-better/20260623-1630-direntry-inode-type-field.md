# DirEntry value-link (inode TYPE field) not exposed by _read_inode's contract

**Category:** Ergonomics gap (model expressiveness)
**Filed by:** test-supervise-sl (os DirEntry fleet, gap-4)
**Date:** 2026-06-23 16:30

## Problem

`DirEntry.is_dir` / `is_file` / `is_symlink` branch on `inode[2]` — the
inode TYPE field (2=dir, 1=file, 3=symlink) — read via
`_filesystem._read_inode(self._inode_num)`. But `_read_inode`'s contract
exposes ONLY the SIZE field (`ensures \result[0] == inode_size(...)`); the
TYPE field (`\result[2]`) has no contract-level predicate. So a caller
cannot express or prove the value link `is_dir() == 1 <=> inode type == 2`.

## Consequence (gap-4 remaining value GAP)

Even with DirEntry now constructible (Strategy C landed — `fs` removed from
the constructor) and the -1-sentinel consequence proven (`formal_os_direntry.py`
PASS for the range + sentinel + is_junction-always-0 consequences), the
VALUE link "mkdir(d); dirent_is_dir(d, ino) == 1" stays **Unknown** — an
honest logged GAP, not a trusted "done".

## Suggested fix

Add an `inode_type` logic function to the UIFS preamble (the twin of
`inode_size`), defined as the big-endian decode of the type field's on-disk
bytes, with a `_read_inode` `ensures \result[2] == inode_type(self.disk,
inode_num)`. This is a definitional zero-TCB addition (mirrors the existing
`inode_size` construction). It would let `is_dir`'s contract carry
`ensures (inode_type(_filesystem.disk, self._inode_num) == 2) ==> \result == 1`,
closing the value-link gap.

(Per the doctrine this is a tooling change — not autonomously trusted; the
`inode_type` function would be a defined logic function, cross-checked like
`inode_size`.)
