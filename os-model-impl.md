# os-model-impl.md — implementation plan for the os functional-correctness model

**Status:** Implementation plan (design + phasing; derives from `os-model-spec.md`)
**Implements:** P1–P4 of `os-model-spec.md` — content fidelity, name resolution, persistence, and the
composite round-trip (`pure_lib_test/formal_0008.py`).

This plan now makes design choices (the spec deliberately did not). Every phase is gated on the full os
proof holding at **0 unproven** and the trusted-axiom base staying **one family** before commit.

---

## 1. The two faithful representations (the central design decision)

The round-trip observes two kinds of byte content. They are modeled differently because they *are*
different:

- **File data is bytes.** A regular file's content genuinely is a byte sequence on disk. So data stays
  **byte-modeled** in the `disk` array; the fidelity property (P1) is the **blit-then-sub disk-slice
  round-trip** — `write` does `Array.blit` (`disk[a:a+n] := c`), a content read does `Array.sub`
  (`result := disk[a:a+n]`), and `sub (blit disk a c) a n = c` is a value-level identity the SMT
  backend already discharges (this is the existing `_block_roundtrip` shape, proven). What is missing
  is only that **no operation returns that slice** — `read` reports a count.

- **A directory name is an identifier, not bytes.** Resolution (P2) must compare "the name I created"
  to "the name I open" by **value**. Forcing this through the 30-byte on-disk encode/decode is the
  Gap-5 wall: `_pad_name`/`_unpack_direntry`/`decode` make the stored name an opaque buffer, so
  `name == pathname` in `_dir_lookup` cannot be discharged. The faithful, tractable model is to track
  the name as a **string value** per directory slot, and resolve against that value. The byte entry in
  block 5 is retained for on-disk-format fidelity but is **not** the resolution path.

**Decision:** data → byte-modeled + a content-returning read; names → value-modeled (string per slot),
resolved by `str_eq`. The byte directory block stays as a format shadow, not the source of truth for
lookup.

## 2. Design choices, concretely

### 2a. Content-returning read (for P1)
Add an operation that returns the bytes read, distinct from the counting `read`:

- a method `sys_pread(fd, nbytes) -> list` (and an `os.pread` wrapper) that resolves the fd's inode and
  first data block exactly as `sys_read` does, then **returns `Array.sub` of the data region** at the
  file offset, rather than only advancing the offset and returning a count.
- `sys_read` (count) is left intact — `formal_0001` and existing callers keep proving; `pread` is the
  content view P1/P4 use. (Replacing `read` wholesale is rejected: it would churn every caller; an
  additive content view is the smaller, safer change.)
- Contract: `ensures \length(\result) == nbytes` (single-block, in-range), and the values are tied to
  the disk slice so the round-trip can equate them to what `write` stored.

### 2b. Value-modeled directory names (for P2)
Give the filesystem a name→slot association that is value-determined:

- add a per-slot **string name** component to the directory model — a parallel `_dir_names`
  (16 string slots for block 5) is the least-invasive shape; a `map string int` (name→inode) is the
  alternative and is cleaner for lookup but a larger representation change. **Start with the parallel
  string array**; revisit the map if lookup proofs want it.
- `_write_entry(slot, inode_num, name)` sets `_dir_names[slot] := name` (the value) alongside the
  existing byte write.
- `_dir_lookup(pathname)` scans `_dir_names[i]` and compares with `str_eq` (`name == pathname`),
  returning the matching slot's inode — instead of decoding opaque bytes. Then "create `f`" stores `f`
  by value and "open `f`" finds it because `str_eq f f` is *Valid* by reflexivity; distinct names
  stay distinct because `str_eq f1 f2` is *false* when `f1 != f2`.
- A class invariant ties `_dir_names`' length to the 16-slot directory, mirroring the existing
  fd-column length invariants.

### 2c. Framed persistence (for P3)
Make the `assigns` clauses precise enough that the operations *between* the write and the content read
provably touch neither the file's data region nor `_dir_names`:

- `close` assigns only `fd_open`; `open` (no-create path) assigns only the `fd_*` columns +
  `next_fd`; `lseek` assigns only `fd_offset`. None list the `disk` data region or `_dir_names`, so the
  written content and the name mapping are framed-invariant across close→open→seek.
- The create path of `open` does assign `disk`/`_dir_names`, but P4's reopen takes the *existing-file*
  path (the file was created on first open), so its frame excludes the data region.

### 2d. Success preconditions (for P4)
The driver must discharge that the success path is taken. It establishes a usable initial state
(capacity for one inode + one block, the target name absent), so `open(O_CREAT)` returns `fd >= 3`,
`write` stores all of `c`, the reopen resolves `f`, and `pread` returns `len(c)` bytes — making the
early `return False` paths provably dead and `\result == True` derivable.

## 3. Phased implementation (each phase gated; each ships a failure-expressible driver)

### Phase 0 — content view + P1 (same fd, single block)
- Add `sys_pread`/`os.pread` (§2a).
- **Driver P1:** open+write `c`, then `pread` from offset 0 → equals `c` (no close/reopen yet).
- **Failure-expressible check:** a variant that `pread`s after writing a *different* buffer must
  **fail** to prove equality — confirming content is observed, not assumed.
- **Gate:** P1 driver *Valid*; full os still 0 unproven; `sys_read`/`formal_0001` unchanged.

### Phase 1 — value-modeled names + P2
- Add `_dir_names` + the length invariant; update `_write_entry` (set the value) and `_dir_lookup`
  (resolve by value) (§2b); audit every `_write_entry`/`_dir_lookup` caller
  (`sys_open`/`sys_mkdir`/`sys_link`/`sys_symlink`/`sys_unlink`/`sys_rename`/…) for the new field's
  frame.
- **Driver P2:** create `f`, then `_dir_lookup(f)` → the created inode; and `_dir_lookup(g)` for an
  absent `g` → −1.
- **Failure-expressible check:** looking up a name never stored must prove −1, not a stale inode.
- **Gate:** P2 driver *Valid*; full os still 0 unproven (all directory-touching syscalls re-proved with
  the new field); corpus byte-clean.

### Phase 2 — framed persistence + P3
- Tighten `close`/`open`/`lseek` `assigns` (§2c); add the frame lemmas/annotations needed so the data
  region and `_dir_names` are provably preserved across them.
- **Driver P3:** write `c`, close, reopen, `pread` → still `c`; and reopen resolves the same inode.
- **Gate:** P3 driver *Valid*; full os still 0 unproven.

### Phase 3 — composite P4 (`formal_0008`)
- Compose P1–P3; the driver discharges the success preconditions (§2d).
- **Gate (acceptance):** `formal_0008` proves `\result == True`; full os 0 unproven; **TCB still one
  family** (no round-trip axiom); `formal_0001` green; corpus byte-clean; doc-coherency green.

## 4. Risks and the hard parts

- **The name representation is invasive (Phase 1).** Every directory-touching syscall must re-prove
  with `_dir_names` in its frame; this is where most regression risk lives. Mitigation: the parallel
  string array mirrors the existing fd-column pattern the os already proves, and the gate is the full
  os holding at 0.
- **Cross-syscall framing (Phase 2)** is the classic difficulty — keeping the data slice and name map
  provably untouched while fd state changes. If `assigns`-level framing is insufficient, a small
  framing lemma per region (data block vs name map vs fd columns, by the disjoint disk regions already
  used elsewhere) is the fallback.
- **Multi-block content is deferred.** P1/P4 target single-block content (`c` ≤ one block), matching
  `formal_0008`'s bound; multi-block read/write fidelity is a later increment under the same P1, and is
  called out rather than silently assumed.
- **`str_eq` reflexivity/discrimination must hold in the model** for the value-name approach; if the
  string theory does not give `str_eq f g` decidably, that is a finding to surface (it would push P2
  toward the name→inode map variant), not a place to add an axiom.

## 5. Sequencing and acceptance

Phase 0 → 1 → 2 → 3, each committed only when its gate is green and the full os holds at 0 unproven.
The work is **done** when `formal_0008` proves `\result == True`, the os is still fully proven with a
single trusted-axiom family, and P1–P3 each have a driver whose postcondition would fail if its
fidelity were violated — so the composite round-trip is established, not vacuous.
