STATUS: OPEN

# Convergence gap — iteration 4 (os syscalls expose NO observable post-state, so functional-consequence formal tests cannot prove)

**Loop:** `config/skills/pycsl-stdlib-coverage` — Step 5 rule "a formal test must verify
the operation's CONSEQUENCE, not merely call it." Surfaced while rewriting the vacuous
return-code formal tests `pure_lib_test/formal_os_dir.py`, `formal_os_query.py`,
`formal_os_io.py` (committed at 668c474) into setup→operate→observe consequence scenarios.
**Iteration:** N = 4.

## Summary

The three `formal_os_*` tests are correctly diagnosed as VACUOUS: each calls one syscall and
asserts that syscall's own return-code disjunction (`\result == 0 or -1`), which is true by the
syscall's `ensures` and proves nothing about the mutation. The skill's prescribed fix — chain a
mutate then OBSERVE the post-state via access/stat/fstat/listdir/read (à la `formal_0001`) — is
**not provable against the current os model**, for ANY syscall, because **no observation call's
contract pins the post-state an observer reads**. The model's syscall `ensures` clauses constrain
ONLY the return code; they say nothing about the resulting disk bytes, fd-table columns, or inode
fields. Therefore a second (observation) call reads a fully unconstrained post-state and the
consequence assertion is Unknown.

This is a model-contract gap, not a tool bug. It is the make-or-break "can PyCSL prove that
writing inode A is reflected when reading it back across two syscalls" question the skill itself
flags (SKILL.md §"What to cover next", the fine-probe gate). The honest answer at the syscall
boundary today is: **no.**

## The three failure modes (all probed, all Unknown)

### 4a — name-keyed observation is opaque (Gap 5)
`mkdir(d, ...)` then `access(d, F_OK)` cannot prove `\result == 1` (present).
Probe (`requires True; assigns _filesystem.disk, _filesystem._mtime_ticks; ensures \result == 1`):
```python
rc = mkdir(d, 0o777)
if rc != 0: return 1
return access(d, F_OK)        # Unknown (0.11s, 186529 steps)
```
**Root cause.** Both `sys_mkdir` and `sys_access` resolve names through
`UnixInodeFileSystem._dir_lookup` (UnixInodeFileSystem.py:591), which decodes on-disk entry
bytes and compares `name == pathname`. The on-disk encoded name **byte content is unmodeled**
(Gap 5 — `str.encode()`/`_pad_name` yield an opaque buffer; `pure_lib/os/UnixInodeFileSystem.py`
`_pad_name` docstring lines 219-232 and `_dir_lookup` cite-note lines 582-590). So the prover
cannot conclude that the entry written under name `d` is the same entry later found under `d`.
Every name-keyed mutate→observe pair (mkdir/rmdir/unlink/link/rename/symlink/truncate/chmod/
chown/utimensat/stat/lstat/access/listdir/scandir/readlink on a symbolic name) hits this wall.

### 4b — fd-keyed observation is not pinned by the mutating syscall's `ensures`
`sys_creat(name, mode)` returns fd; `sys_fstat(fd)` cannot prove `0 <= ino < 32`.
Probe (locally-constructed `fs = UnixInodeFileSystem()`):
```python
fd = fs.sys_creat(name, mode)
if fd < 3: return 1
ino = fs.sys_fstat(fd)
if ino >= 0 and ino < 32: return 1
return 0                       # Unknown (0.11s, 316047 steps)
```
**Root cause.** `sys_creat` is `#@ no_inline` (UnixInodeFileSystem.py:1310-1318) and its only
post-call fact is `ensures \result == -1 or \result >= 3` — it does NOT promise
`fd_inode[\result]` is a valid inode. `sys_fstat` (UnixInodeFileSystem.py:1246) returns
`fd_inode[fd]`, which the prover sees as unconstrained. Even the lone non-name fd round-trip the
skill suggests (dup → read the same bytes) fails the same way: `sys_read`'s contract is
`ensures \result == -1 or (\result >= 0 and \result <= nbytes)` (UnixInodeFileSystem.py:833-836)
— a byte-COUNT bound, with NO claim that the bytes equal what was written, and no claim the count
equals the written length. So `back == len(data)` after dup+write+read is Unknown
(Timeout 30s, 16.2B steps when isolated).

### 4c — a freshly-constructed instance has no known initial state
`UnixInodeFileSystem()` then `fs.sys_fstat(fd)` for `fd >= 3` cannot prove `\result == -1`
(no fd open on a fresh fs). Probe: Unknown (0.11s, 306766 steps).
**Root cause.** `UnixInodeFileSystem.__init__` (UnixInodeFileSystem.py:322) carries **no contract
at all** — no `ensures`. The class invariant pins only lengths (`\length(self.fd_open) == 64`,
etc.) and a few `>= 0` bounds, never the contents (`fd_open` all-zero, root inode present). So a
constructed instance's observable state is unconstrained; no "fresh fs ⇒ X is absent/closed"
baseline can be asserted.

## What CAN be proven (and what the rewrites therefore assert)

The strongest provable property at the formal-test boundary remains each syscall's **return-code
totality/safety contract** — i.e. exactly what 668c474 asserted. The skill's own flagship
`formal_0001` only proves the byte-COUNT round-trip survives (`count == len(data)` via the read
return value), and even that leans on the same `read` count bound; it does NOT prove content
(`formal_0008`, which tries `back == c`, does not currently prove from this CWD — int-vs-array
type error, a separate pre-existing committed defect).

A genuine intra-body round-trip IS provable: `UnixInodeFileSystem._block_roundtrip`
(UnixInodeFileSystem.py:498-521) proves `\array_eq(\result, data)` because the write
(`Array.blit`) and read-back (`Array.sub`) are in ONE method body. Its own cite-note (lines
506-514) states it "Does NOT cover the cross-syscall open/write/close/open/read path." That is
precisely this gap, acknowledged in the model.

## Proposed fix (model-side, NOT in scope for pure_lib_test/, and the os model is frozen)

To make consequence-style formal tests provable, the mutating syscalls must expose post-state in
their contracts, and names must be value-modeled:
1. **fd-keyed (unblocks 4b/4c):** give `sys_creat`/`sys_open` an `ensures` pinning
   `fd_open[\result] == 1` and `0 <= fd_inode[\result] < 32` (when `\result >= 3`); give
   `__init__` an `ensures \forall i; 0 <= i < 64 ==> fd_open[i] == 0`. Then dup→fstat and
   creat→fstat become provable. For content, `sys_read`/`sys_write` would need a stronger contract
   relating the read bytes to the written bytes (a disk-content `ensures`), which is the hard part.
2. **name-keyed (unblocks 4a):** close Gap 5 — value-model the on-disk encoded name bytes so
   `_dir_lookup`'s `name == pathname` round-trips. This is a large, deep change to the byte model.

Both touch the FROZEN os model (`pure_lib/os/`), which this agent must not perturb. Hence the gap
is documented, not implemented.

## Disposition of the rewrites this iteration

Per the loop's "do NOT fall back to the vacuous return-code form and do NOT weaken to True — keep
the strongest consequence form you CAN prove (commented)" rule: the three `formal_os_*` files are
rewritten to **structure each test as a setup→operate→observe SCENARIO** (the chained calls that a
consequence test would use) with the desired consequence assertion written as a COMMENT, while the
asserted, provable `ensures` is the syscall's return-code/safety contract over the whole chain —
which now at least exercises the mutate+observe call sequence rather than a single bare call.
Each test names, in a comment, the exact consequence it WOULD assert and points to this gap doc.
`getpid`/`fsync` are kept as honestly-labelled non-functional (constant / flush) assertions.
