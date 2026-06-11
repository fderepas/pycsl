# 11-1804-convergence-gap-14 — Phase 3 fd-chain + content consequences unprovable through the public API

STATUS: OPEN — model-side gap (analogous to the gap-7 namespace post-state, now for the fd chain + content).

**Loop:** `config/skills/pycsl-stdlib-coverage` — Step 5 ("a formal test must
CALL THE API and verify a CONSEQUENCE, not a return code"). Phase 3 of
`stronger-than-os.md` (the fd chain + the write→read==data content round-trip).

**Test agent role:** wrote API-only consequence tests in `pure_lib_test/formal_os_fd.py`
(and inspected `pure_lib_test/formal_0008.py`). Did NOT edit `pure_lib/os/` or
`src/pycsl/`. Did NOT weaken to a return-code assertion, simulate, or touch internals.

---

## What won't prove (the 5 Phase-3 consequences)

`pure_lib_test/formal_os_fd.py` calls ONLY the public API (`open`, `read`,
`write`, `close`, `lseek`, `fstat`, `dup` + flag constants). Every theorem is a
setup→operate→OBSERVE scenario asserting the operation's promised post-state.
Running it (`--keep-mlw`, Alt-Ergo 2.6.2 → Z3 4.13.3) gives:

| # | Theorem (consequence) | Final Postcondition goal | Symptom |
|---|---|---|---|
| 1 | `open_existing_yields_valid_fd` — `open(existing, O_RDONLY) >= 3` | **Timeout (30s, 15.5M steps)** | Unknown |
| 2 | `open_absent_yields_enoent` — `open(absent, O_RDONLY) == -1` | **Timeout (30s, 19.5M steps)** | Unknown |
| 3 | `fstat_of_opened_fd_is_valid_inode` — `0 <= fstat(open(p)) < 32` | **Timeout (30s, 19.4M steps)** | Unknown |
| 4 | `content_round_trip` — write(c)→close→reopen→read; count round-trips | **Timeout (30s, 19.3M steps)** | Unknown |
| 5 | `dup_yields_valid_fd` — `dup(valid_fd) >= 3` | **Timeout (30s, 16.0M steps)** | Unknown |

All other VCs in the file are **Valid** (preconditions, the early-out
postconditions, the `UnixInodeFileSystem`/`_filesystem` type invariants). The
Timeout on each function's *final* Postcondition sub-goal is the prover
manifesting Unknown: it cannot relate the observed value to the operation, so it
explores the unconstrained post-state until the 30 s budget is exhausted.

`--no-typecheck`/emission is clean (the earlier `int`-vs-`bool` emission snag was
resolved by giving each theorem an `int` return + `\result == 1`, matching the
`formal_os_namespace.py` convention; the older gap-4 `int`-vs-array type error on
`formal_0008` no longer reproduces here).

## Minimal API-only reproducer

```python
from pure_lib.os import open, O_RDONLY, O_CREAT, O_WRONLY, close

#@ requires True
#@ ensures \result == 1
def open_existing_yields_valid_fd(p: str) -> int:
    fd0 = open(p, O_CREAT | O_WRONLY, 0o777)   # setup: create p
    if fd0 < 3:
        return 1
    close(fd0)
    fd = open(p, O_RDONLY, 0o777)              # operate: reopen existing
    if fd >= 3:                                # OBSERVE: valid fd
        return 1
    return 0
# => final Postcondition goal: Timeout / Unknown.
```

## Root cause — the fd/content syscall contracts are return-code / byte-count only (cite `pure_lib/os/__init__.py`)

The public contracts expose **no fd→inode resolution and no content post-state**:

```
open(filepath, flags, mode):  #@ ensures \result == -1 or \result >= 3   (line 279)
read(fd, n):   #@ ensures \result == -1 or (\result >= 0 and \result <= n)   (line 287)
write(fd, data): #@ ensures \result == -1 or \result >= 0   (line 294)
fstat(fd):  #@ ensures \result == -1 or (\result >= 0 and \result < 32)   (line 153)
lseek(fd, pos, how): #@ ensures \result >= -1   (line 173)
dup(fd):  #@ ensures \result == -1 or \result >= 3   (line 146)
```

Consequence by consequence:

- **(1) open-valid / (2) open-ENOENT.** `open`'s ensures is a bare disjunction
  `-1 or >= 3` with **no discriminant on path existence**. So the prover cannot
  conclude that an *existing* path yields `>= 3` (it may be `-1`), nor that an
  *absent* path yields `-1` (it may be `>= 3`). There is no `ENOENT` direction —
  unlike the namespace mutators, whose post-gap-7 contracts now carry
  `dir_lookup(...)`-keyed ensures (see `access`/`link`/`rename`/`remove` lines
  123, 161, 260, 302). `open` carries no analogous `dir_lookup`-keyed clause.
- **(3) fstat→inode.** `fstat`'s ensures bounds the inode (`0 <= r < 32`) but
  **does not tie it to the path `open` walked**, and `open` does not pin the fd
  `>= 3` for an existing file — so even the bounded-inode observation is not
  entailed (the `fd < 3` early-out keeps the theorem from being vacuously
  Valid, exposing the wall).
- **(4) content round-trip (the flagship).** `read` returns a **byte COUNT**
  (`\result <= n`), NOT the bytes, and `write`'s ensures has **no content
  post-state** ("the inode now holds `data`"). So the model cannot even *name*
  "the bytes read == the bytes written" — the true equality is inexpressible
  through the count-returning `read`. The weakest nameable shadow (the
  round-tripped count equals `len(c)`) is itself Unknown because the count is
  unlinked to `write`'s data and to `open`'s fd validity.
- **(5) dup shared offset.** `dup`'s ensures (`-1 or >= 3`) carries **no link to
  the source fd's open-file-description**, so neither validity-given-a-valid-
  source nor the shared-offset behaviour (a write through one fd seen at the
  other's offset) is entailed.

This is the **fd-chain / content analogue of gap-7's namespace post-state**: gap-7
added `dir_lookup(_filesystem.disk, 5, name)`-keyed ensures so name-keyed
consequences (`mkdir→access PRESENT`, `unlink→ABSENT`, …) now prove
(`formal_os_namespace.py` is **Valid** today). The fd chain + content has not yet
received the equivalent observable post-state.

## Proposed fix (MODEL-side — `pure_lib/os/` + `UnixInodeFileSystem.py`, NOT the test)

Mirror the gap-7 namespace pattern, one rung lower (the fd-table → open-file-
description → inode chain, and the content view), per `stronger-than-os.md` §2/§4
Phase 3. Concretely, give the syscall contracts an **observable post-state** via
abstract logic views (the way `dir_lookup` was added for the namespace):

1. **fd→inode resolution view.** Add a logic function
   `fd_resolves(disk/fd_table, fd) : inode` (or expose `fd_inode[fd]`) and have:
   - `open` ensure, on success, `\result >= 3` **and**
     `fd_resolves(open(p)) == dir_lookup(disk, 5, p)` (the fd resolves to the
     inode the path names — composing on the now-proven namespace view), and on
     failure `\result == -1 <==> dir_lookup(disk, 5, p) < 0` (the ENOENT
     discriminant — the dual of gap-7's presence view, here gating open's `-1`).
   - `fstat` ensure `\result == fd_resolves(fd)` so theorem (3) composes.
2. **content view (the round-trip).** Add an abstract content map
   `inode_content(disk, ino) : array int` (or `byte_at(disk, ino, off)`), and:
   - `write(fd, data)` ensure (on success) that `inode_content` at the fd's
     resolved inode now equals/contains `data` at the fd's offset — the
     write post-state.
   - `read(fd, n)` must **return the bytes**, not just a count (or expose a
     companion content view), so `read(fd, n) == slice(inode_content(...), off, n)`
     is expressible. With both, `content_round_trip` discharges as
     `read-back == data` (the flagship equality), not merely the count.
   - `lseek` ensure the offset post-state (`fd_offset[fd] == pos` for `SEEK_SET`)
     so the round-trip's `lseek(0)` is pinned.
3. **dup shared offset.** `dup` ensure the new fd shares the source's
   open-file-description: `fd_resolves(dup(fd)) == fd_resolves(fd)` and the two
   share one offset cell, so a write through one is seen at the other.

The byte-level content layout (like the dirent byte layout in gap-7/§3) can be
presented behind `#@ interface` as the abstract content map and **refined or
TCB-ledgered underneath** if the `str.encode()`/byte round-trip gap (Gap 5)
blocks the concrete byte proof. The inductive part of the content round-trip (a
write of an N-element array seen element-wise by read) may need a Rocq+Lean
agreement lemma, as the namespace uniqueness did.

Until then, the 5 theorems in `formal_os_fd.py` are the **honest, API-calling,
Unknown** form of the Phase-3 consequences — kept as the standing frontier, NOT
weakened to return-code assertions.

## Note on `formal_0008.py` (the prior content-round-trip target)

`pure_lib_test/formal_0008.py` does NOT simulate, but it is **not internals-blind**:
it imports `_filesystem` from `pure_lib.os` and names it in its `assigns` clause
(`_filesystem.disk, _filesystem.fd_open, _filesystem.fd_inode, _filesystem.fd_offset,
_filesystem.fd_flags, _filesystem.next_fd`). It calls the API for the operations
(`open`/`write`/`close`/`lseek`/`read`) but reaches into the fd-table/disk
internals to frame them, and asserts `\result == True` on the read-back equality
`back == c` (which is the right consequence but blocked by the same content-view
gap above). The internals-blind, API-only restatement of this flagship is
`content_round_trip` in `formal_os_fd.py` (case 4). Recommend retiring/folding
`formal_0008.py` into `formal_os_fd.py` once the model gains the content view —
leaving it as-is for now (test agent does not edit it beyond inspection per scope,
and does not commit).
