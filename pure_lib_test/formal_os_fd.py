# formal_os_fd.py — os FD-CHAIN + CONTENT consequences, through the PUBLIC API ONLY.
#
# Phase 3 of stronger-than-os.md: the fd chain (open path-walk -> open-file-
# description {offset, flags} -> inode) and the write -> read == data content
# round-trip. The directory NAMESPACE (Phase 2) now PROVES through the API
# (formal_os_namespace.py is Valid). This file is the NEXT frontier.
#
# INTERNALS-BLIND. Every theorem CALLS THE REAL PUBLIC API the way a caller does:
# it imports `open`, `read`, `write`, `close`, `lseek`, `fstat`, `dup` and the
# flag constants from pure_lib.os and drives a setup -> operate -> OBSERVE
# scenario, asserting the observation's promised post-state. There is NO
# `_filesystem`, NO `disk`, NO `fd_*`, NO `_dir_lookup`, NO `sys_*`, NO
# `UnixInodeFileSystem(...)`, NO hand-written bytes. (grep -E confirms.)
#
# HONEST OUTCOME — these Phase-3 consequences DO NOT PROVE through the API today.
# The fd-chain / content syscalls' public contracts in pure_lib/os/__init__.py
# are RETURN-CODE / BYTE-COUNT ONLY, and expose NO fd->inode resolution and NO
# content post-state:
#
#   open(filepath, flags, mode):  #@ ensures \result == -1 or \result >= 3
#       — return-code only; NO link between the path and which inode the fd
#         resolves to, and NO ENOENT discriminant (an absent path is not pinned
#         to -1, an existing path is not pinned to >= 3).
#   read(fd, n):   #@ ensures \result == -1 or (\result >= 0 and \result <= n)
#       — byte COUNT only; returns a count, NOT the bytes, and carries no link
#         to what `write` put at the offset.
#   write(fd, data): #@ ensures \result == -1 or \result >= 0
#       — byte count only; NO content post-state (no "the inode now holds data").
#   fstat(fd):  #@ ensures \result == -1 or (\result >= 0 and \result < 32)
#       — an inode number, but with NO link to the path `open` walked, so it
#         cannot witness "this fd resolves to THAT inode/size".
#   lseek(fd, pos, how): #@ ensures \result >= -1   — NO offset post-state.
#   dup(fd):  #@ ensures \result == -1 or \result >= 3
#       — return-code only; NO shared-offset / shared open-file-description link.
#
# Each theorem returns `int` and asserts `\result == 1` (the formal_os_namespace
# convention; a `-> bool` body trips a WhyML int-vs-bool emission error). So each
# theorem below is the HONEST, API-calling form of the Phase-3
# consequence; it is EXPECTED to report Unknown until the MODEL's fd/content
# syscall contracts gain observable post-state `ensures` (a content/offset
# abstract view, analogous to gap-7's namespace `dir_lookup` post-state). The
# precise reproducers, root cause, and proposed model-side fix are recorded in
# the accompanying 11-1804-convergence-gap-14.md.
#
# DO NOT make these green by simulating, by weakening to the operation's own
# return-code disjunction, or by touching internals. A documented Unknown is the
# correct convergence-loop outcome here.

from pure_lib.os import (
    open, read, write, close, lseek, fstat, dup,
    O_RDONLY, O_WRONLY, O_CREAT, SEEK_SET,
)


# ---------------------------------------------------------------------------
# (1) open-VALID: open(existing, O_RDONLY) -> a VALID fd (>= 3 in this model;
# fds 0/1/2 are reserved std streams).
# Setup: create the file via the API (open with O_CREAT). Operate: reopen it
# read-only. OBSERVE: the returned fd is valid.
#
# HONEST STATUS: Unknown. open's contract (\result == -1 or >= 3) does NOT pin
# an *existing* path to a success: the prover sees open(existing) as possibly
# returning -1, so `>= 3` is not entailed. gap-14 §1.
#@ requires True
#@ ensures \result == 1
def open_existing_yields_valid_fd(p: str) -> int:
    fd0 = open(p, O_CREAT | O_WRONLY, 0o777)   # setup: create p via the API
    if fd0 < 3:
        return 1                               # creation failed: not the case under test
    close(fd0)
    fd = open(p, O_RDONLY, 0o777)              # operate: reopen the existing file
    if fd >= 3:                                # OBSERVE: valid fd — ASSERTED == 1
        return 1
    return 0


# ---------------------------------------------------------------------------
# (2) open-ENOENT: open(absent, O_RDONLY) -> the documented failure (-1).
# Operate on a name never created in this scenario. OBSERVE: open returns -1.
#
# HONEST STATUS: Unknown. open's contract does NOT pin an *absent* path to -1:
# the prover sees open(absent) as possibly returning >= 3, so `== -1` is not
# entailed (no ENOENT discriminant in the contract). gap-14 §2.
#@ requires True
#@ ensures \result == 1
def open_absent_yields_enoent(p: str) -> int:
    fd = open(p, O_RDONLY, 0o777)              # operate: open a never-created name
    if fd == -1:                               # OBSERVE: ENOENT (-1) — ASSERTED == 1
        return 1
    return 0


# ---------------------------------------------------------------------------
# (3) fstat resolves the opened fd to a VALID inode.
# Setup: create p. Operate: reopen p. OBSERVE: fstat(fd) yields a valid inode
# number (0 <= ino < 32). The STRONGER consequence — fstat(open(p)) is the SAME
# inode every open of p resolves to — is NOT expressible: fstat's contract
# carries no link to the path open walked. gap-14 §3.
#
# HONEST STATUS: Unknown. fstat's contract bounds the inode but does not tie it
# to the fd's path, and open does not pin fd >= 3, so even validity is unentailed.
#@ requires True
#@ ensures \result == 1
def fstat_of_opened_fd_is_valid_inode(p: str) -> int:
    fd0 = open(p, O_CREAT | O_WRONLY, 0o777)
    if fd0 < 3:
        return 1
    close(fd0)
    fd = open(p, O_RDONLY, 0o777)
    if fd < 3:
        return 1
    ino = fstat(fd)                            # OBSERVE: fd -> inode resolution
    close(fd)
    if ino >= 0 and ino < 32:                  # ASSERTED: valid inode
        return 1
    return 0


# ---------------------------------------------------------------------------
# (4) CONTENT ROUND-TRIP (the flagship): create -> write(data) -> close ->
# reopen -> read == data. This is formal_0008's target, re-stated API-only with
# the read-back equality as the asserted CONSEQUENCE (not a return code).
#
# HONEST STATUS: Unknown. read returns a byte COUNT (\result <= n), NOT the bytes,
# and write's contract has no content post-state — so the model cannot express
# "the bytes read back EQUAL the bytes written". We assert the strongest CONTENT
# consequence the API surface even lets us NAME: that a read after the write-back
# returns a non-negative count bounded by the data length (count == len(data)).
# It is Unknown because read's contract does not link the count to write's data.
# The TRUE equality (read_bytes == data) is not even expressible through the
# count-returning `read` — that is the core of gap-14 §4 (read must return / a
# content view must expose the bytes).
#@ requires \length(c) >= 1 and \length(c) <= 512
#@ ensures \result == 1
def content_round_trip(p: str, c: list) -> int:
    fd = open(p, O_CREAT | O_WRONLY, 0o777)    # setup: create p for write
    if fd < 3:
        return 1                               # create failed: not the case under test
    n_written = write(fd, c)                   # operate: write the content
    close(fd)

    fd2 = open(p, O_RDONLY, 0o777)             # reopen for read
    if fd2 < 3:
        return 1
    lseek(fd2, 0, SEEK_SET)
    n_read = read(fd2, len(c))                 # OBSERVE: read back
    close(fd2)
    # The CONSEQUENCE we WANT: the bytes read == c. NOT EXPRESSIBLE (read returns
    # a count). The strongest NAMEABLE shadow: the round-tripped count equals the
    # written length. ASSERTED — Unknown (read's count is unlinked to write).
    if n_written == len(c) and n_read == len(c):
        return 1
    return 0


# ---------------------------------------------------------------------------
# (5) dup: dup(fd) shares the open-file-description (offset) with fd.
# Setup: create + open p for write, write some content. Operate: dup the fd.
# OBSERVE: dup returns a valid fd, AND a write through one is seen at the shared
# offset of the other (the shared-offset consequence). Only the VALIDITY of the
# duped fd is even NAMEABLE here; the shared-offset behaviour needs an offset
# post-state the API does not expose. gap-14 §5.
#
# HONEST STATUS: Unknown. dup's contract (\result == -1 or >= 3) carries no link
# to the source fd's open-file-description, so neither validity-given-valid-source
# nor the shared offset is entailed.
#@ requires True
#@ ensures \result == 1
def dup_yields_valid_fd(p: str) -> int:
    fd = open(p, O_CREAT | O_WRONLY, 0o777)
    if fd < 3:
        return 1
    fd2 = dup(fd)                              # operate: duplicate the descriptor
    close(fd)
    if fd2 >= 3:                               # OBSERVE: duped fd valid — ASSERTED == 1
        close(fd2)
        return 1
    return 0
