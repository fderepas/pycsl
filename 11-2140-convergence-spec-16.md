# 11-2140-convergence-spec-16 — TOOL-AGENT (SPEC PHASE) spec for gap-16 content round-trip

STATUS: DRAFT

**Loop:** `config/skills/pycsl-stdlib-coverage` Step 5b (the Rocq+Lean valve for an SMT-inductive wall). Input: `11-2140-convergence-gap-16.md`. Target: flip `content_round_trip` (`pure_lib_test/formal_os_fd.py`) — the Phase-3 flagship — or name the honest next gap.

**Scope discipline (this phase):** validate the lemma in both kernels; specify registration + citation; analyze the reopen link; give a feasibility verdict. **NO source edits made. No git commit/push. No implementation.** Probes under `/tmp/gap16/` only.

---

## 1. The validated lemma `UnixFs.Content.write_then_read_agree` (make-or-break #1 — PASSES)

### 1.1 WhyML statement (transcribed from gap-16 §3, the registry form)

Backing symbol `content_block (disk: array int) (blk: int) (i: int) : int` (the concrete twin of the namespace's abstract `dir_lookup`, one rung lower onto file CONTENT), defined `content_block disk blk i = disk[blk*512 + i]`. The lemma:

    forall disk blk data m i.
      6 <= blk < 256  ->  0 <= m <= 512  ->  m = length data  ->
      (forall j. 0 <= j < m -> (blit_write disk blk data)[blk*512 + j] = data[j])  ->
      0 <= i < m  ->
      content_block (blit_write disk blk data) blk i = data[i]

i.e. after writing `data` into block `blk`, the content view of `blk` equals `data` element-for-element. The blit post-state is carried as an EXPLICIT antecedent (the `forall j` hypothesis), exactly as gap-9's `scan_reflects_present` carries `slot_inode_nonneg` and gap-11/12 carry their frame/witness hypotheses — keeping the registered axiom faithful (not over-strong) and matching the family's trust KIND.

### 1.2 Rocq proof — ACCEPT

`/tmp/gap16/WriteThenReadAgree.v` (Module `UnixFs.Content`, `Section Blit`). Modeled FAITHFULLY as a CONCRETE byte-by-byte blit, NOT by assuming the post-state:
- `disk := Z -> Z` (functional byte map), `rd d b := d b`, single-byte store `upd` with the standard `get_of_set_eq` / `get_of_set_neq` laws (the `Array.get_of_set` the sketch names).
- `blit_n d off k` = write `dat[0..k)` into `d` at consecutive offsets, by structural recursion on the write count.
- `blit_read_back` proven by `induction k` + per-index case split (`Nat.eq_dec j k'`) on `get_of_set_eq` / `get_of_set_neq` — the structural-induction-over-the-byte-index discharge of the SMT wall.
- `content_block d blk i := rd d (blk*512 + i)`; `write_then_read_agree` instantiates `off = blk*512`, closing by `apply blit_read_back`.

**Result:** `coqc 8.20.1` compiles clean. `Print Assumptions write_then_read_agree` reports ONLY the abstract `Section Variable dat : Z -> Z` — **no Axiom, no Admitted**. This is "Closed under the global context" modulo the abstract data map, identical to the discipline of `EmptyDiskSlotsDead.v` / `UnixDirScan.v` (whose `rd` / `slot_inode` are likewise abstract Section Variables). The registered uninterpreted `content_block` is the abstraction of this concrete read-after-write fact via `content_block d blk i = rd d (blk*512 + i)`.

### 1.3 Lean proof — ACCEPT

`/tmp/gap16/WriteThenReadAgree.lean` — structural mirror (functional `Disk := Int -> Int`, `upd` with `get_of_set_eq`/`get_of_set_neq` via `simp`, `blitN` recursive, `blit_read_back` by `induction k` + `by_cases j = k'` + `omega`, the `Array.getElem_set`-shaped simp discharge).

**Result:** `lean 4.30.0` (core only, no Mathlib) compiles; `#print axioms write_then_read_agree` = `[propext, Quot.sound]` ⊆ allowlist `{propext, Quot.sound, Classical.choice}`, **no sorry**.

### 1.4 Faithfulness note

The proof models the REAL `_block_roundtrip`/blit semantics: each written index is set exactly once (the recursion writes `off+k'` at step `S k'`), and the read-back is the same functional `rd`, so it reflects `disk[blk*512+i] := data[i]` followed by `disk[blk*512+i]` read-back — NOT an over-claim. It does NOT assert anything about multi-block layout, the inode decode, or the namespace; it is precisely the single-block read-after-write byte agreement gap-16 §3 names. The blit post-state hypothesis is exactly what `sys_write`'s already-body-proven loop invariant (`pure_lib/os/UnixInodeFileSystem.py:1221`) establishes, so the lemma composes with the existing write-side proof rather than re-deriving it.

**Lemma verdict: BOTH KERNELS ACCEPT. Make-or-break #1 is satisfied.**

---

## 2. THE REOPEN LINK (make-or-break #2 — the feasibility crux): DOES NOT CLOSE the round-trip

### 2.1 The trace (`content_round_trip`)

`pure_lib_test/formal_os_fd.py` `content_round_trip`:

    fd  = open(p, O_CREAT|O_WRONLY)   # sys_open: alloc inode I, fd_inode[fd]=I, fd_block[fd]=inode[8]=0
    write(fd, c)                       # sys_write: blit c into block B; inode[0]:=len(c); inode[8]:=B; _write_inode(I)
    close(fd)                          # sys_close: clears fd_open[fd] ONLY — disk/inodes untouched (correct)
    fd2 = open(p, O_RDONLY)            # sys_open: inode_num = _dir_lookup(5,p); fd_inode[fd2]=inode_num; fd_block[fd2]=_read_inode(inode_num)[8]
    n_read = read(fd2, len(c))         # sys_read: size=_read_inode(fd_inode[fd2])[0]; returns min(len(c), size-0)

Test asserts `n_written == len(c) and n_read == len(c)`.

### 2.2 Where the chain breaks — and what the lemma does NOT reach

The lemma in §1 proves the **content byte** agreement: `disk[B*512+i] == c[i]`. The data blocks are NOT wiped by `close` (`sys_close` `pure_lib/os/UnixInodeFileSystem.py` touches only `fd_open`), so on-disk the bytes survive. So far so good — but the test's `n_read == len(c)` conjunct does NOT depend on the byte content at all. It depends on the **inode SIZE**:

    n_read = min(len(c), inode_reopened[0] - 0)   where inode_reopened = _read_inode(_dir_lookup(5, p))

For `n_read == len(c)` we need `_read_inode(_dir_lookup(5, p))[0] == len(c)` (and `len(c) <= that size`). The write set `inode[0] = len(c)` on inode `I`. **But the reopen resolves `inode_num = _dir_lookup(5, p)` — an ABSTRACT inode number whose CONTRACT (`sys_open` ensures, `:1115`) binds only `fd_inode[result] == dir_lookup(self.disk, 5, pathname)` and `0 <= fd_inode[result] < 32`. There is NO contract that `dir_lookup(disk,5,p) == I` (the inode the create allocated), and NO contract/class-invariant that `_read_inode(dir_lookup(...))[0] == len(c)`.** I confirmed there is no inode-size class invariant (`:435–444` are length/range/uid invariants only; none relate an inode's on-disk `inode[0]` to any name-resolvable quantity).

So the abstract `dir_lookup` reopen SEVERS the size→content-length linkage. This is the spec-risk-6.2 fidelity (on-disk-bytes ↔ abstract-decode ↔ reopened-inode-size) the cross-check cannot machine-derive. **`content_round_trip'vc` Postcondition is Unknown — reproduced** (312264 steps, 0.13s; alongside the out-of-scope `open_absent_yields_enoent` Unknown from gap-14 §2). open_existing/fstat/dup remain Valid (no regression).

### 2.3 Why the §1 lemma alone does NOT flip the test

The §1 lemma is necessary for the TRUE byte equality `read_bytes == c` (which is additionally not nameable through the count-returning `read` — POSIX `os.read` returns bytes, this model returns a count). But the test as written asserts the COUNT shadow `n_read == len(c)`, which is gated by the **inode SIZE round-trip across the abstract reopen**, NOT by the byte content. The byte-content lemma proves the wrong half of the wall for this particular assertion. Even if `read` were rewritten to return bytes and assert `read_bytes == c`, that equality would STILL require the reopened block pointer `inode_reopened[8]` to equal the written `B` AND the reopened size to equal `len(c)` — both severed by the same abstract `dir_lookup`.

### 2.4 FEASIBILITY VERDICT: a MULTI-GAP ARC, not a bounded fix

gap-16 does **NOT** close the content round-trip with "lemma + inode-keyed content view + close-frame". The lemma passes and the close-frame is real (close only touches the fd table), but the **reopen link is a deeper wall, not a bounded frame**. Two distinct severances must be bridged, neither of which the §1 byte lemma reaches:

1. **NAME→INODE persistence across create/reopen.** `_dir_lookup(5, p)` after `close` must resolve to the SAME inode `I` the `O_CREAT` open allocated and `_write_entry`'d. This is exactly the directory-scan REFLECTION already cross-validated as `UnixFs.Dir.scan_reflects_present` / `insert_preserves_unique` — but those give EXISTENCE/uniqueness of a live slot, NOT the identity `dir_lookup(post-create disk, 5, p) == I`. A new lemma is needed: **`UnixFs.Dir.lookup_after_insert_recovers_inode`** — after `_write_entry(5, slot, I, p)` (and no intervening directory mutation), `dir_lookup(disk', 5, p) == I`. This is the "insert then lookup recovers the inserted inode" companion of the existing absence/uniqueness axioms; it is a finite slot case-split (no new induction beyond the scan), highly likely to cross-validate, BUT it is a SEPARATE registered axiom — a distinct gap.

2. **INODE-keyed SIZE/CONTENT view surviving `_write_inode`/`_read_inode` round-trip.** Given inode identity `I`, the reopened `_read_inode(I)[0]` must equal the `len(c)` the write stored. The inode round-trip `_read_inode(_write_inode inode)[k] == inode[k]` is ALREADY the `UnixFs.Struct.i18.round_trip` axiom (used for `inode[8]` block recovery per gap-16 §3) — it extends to `inode[0]` (size) the same way (same packed-struct field round-trip, no new induction). This is a registration/citation extension, the closest to "bounded". But it must be COMPOSED with (1): the model must carry, across the close/reopen, an inode-keyed view `inode_size(disk, I) = _read_inode(I)[0]` and a class invariant or frame that `inode_size` is preserved by everything between write and reopen (close, the second open's create-skip path). That composition — an inode-keyed `inode_content`/`inode_size` LOGIC FUNCTION threaded through `sys_write` (sets it), `sys_close` (frames it), `sys_open` (recovers it via `lookup_after_insert_recovers_inode` + `i18.round_trip`), `sys_read` (reads it) — is the structural work that does NOT exist today and is NOT a single frame.

**Next gap named precisely (gap-17):** introduce the inode-keyed logic functions `inode_size(disk, ino)` / `inode_content(disk, ino, i)` in `_AXIOM_FUNCTIONS`, register **`UnixFs.Dir.lookup_after_insert_recovers_inode`** (name→inode identity across create) and cite the EXISTING `UnixFs.Struct.i18.round_trip` for `inode[0]`/`inode[8]` recovery, then thread an inode-keyed size/content view (with a close-frame and a create-skip-path frame) through `sys_write`/`sys_close`/`sys_open`/`sys_read` so the reopened size composes back to `len(c)`. Only then does `n_read == len(c)` (and, with a byte-returning read, the §1 byte equality) become derivable. gap-16's §1 lemma is a PREREQUISITE BRICK of that arc — landing it is real progress — but it is NOT the keystone for THIS test's assertion.

**Bottom line: lemma PASSES both kernels (real, registerable progress); the reopen link is a DEEPER MULTI-GAP ARC. gap-16 alone does not flip `content_round_trip`. Next: gap-17 (inode-identity-across-reopen + inode-keyed size/content view).**

---

## 3. Registration + os citation plan (for the implementing tool-agent, NOT done here)

### 3.1 `_AXIOM_REGISTRY` (`src/pycsl/module6_whyml/preamble.py`)

Add entry `"UnixFs.Content.write_then_read_agree"` with the §1.1 WhyML body. Follow the existing comment discipline (cite the `/tmp/gap16/WriteThenReadAgree.{v,lean}` → permanent `unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/WriteThenReadAgree.{v,lean}`; note Rocq Print Assumptions = abstract Section Variable only, Lean axioms ⊆ allowlist; state the blit post-state antecedent is faithful/explicit). It is NOT a class-inv axiom (no `_CLASS_INV_AXIOMS` entry — it constrains content, not the directory-uniqueness invariant).

### 3.2 `_AXIOM_FUNCTIONS` (`src/pycsl/module6_whyml/preamble.py`)

Add prefix `"UnixFs.Content."` →
- `val function content_block (disk : array int) (blk : int) (i : int) : int`

For the gap-17 arc (NOT gap-16): also
- `val function inode_size (disk : array int) (ino : int) : int`
- `val function inode_content (disk : array int) (ino : int) (i : int) : array int` (or keyed `(disk, ino, i) : int`)

and register `UnixFs.Dir.lookup_after_insert_recovers_inode` reusing the SAME `slot_inode`/`slot_name`/`dir_lookup` symbols (no new function decl).

### 3.3 os citation

- `sys_write` (`pure_lib/os/UnixInodeFileSystem.py:1195`): its content ensures `disk[fd_block[fd]*512+i] == data[i]` is the blit-post-state ANTECEDENT of `write_then_read_agree`; cite it to bind `content_block(disk, fd_block[fd], i) == data[i]`. (The fd-keyed `disk[fd_block[fd]*512+i]` view stays the concrete one; `content_block` is its registered abstraction so it survives the reopen via inode identity — gap-17.)
- `sys_read` (`:1276`): cite the content link so the returned count is tied to `content_block` of the reopened block. CURRENT model is fd-keyed (`disk[fd_block[fd]*512+i]`); gap-17 swaps to the **inode-keyed** `inode_content(disk, fd_inode[fd], i)` so the view is INDEPENDENT of which fd opened it — the structural change that lets read-after-reopen compose. (gap-16's `content_block` is the per-block half; inode-keying is gap-17.)
- `sys_open` (`:1163`, `fd_block[fd] = inode[8]`): under gap-17, cite `i18.round_trip` (`inode[8]` recovery) + `lookup_after_insert_recovers_inode` so the reopened `fd_block`/`fd_inode` recover the written values.

---

## 4. Gate + RISKS

### 4.1 Gate

- [x] BOTH kernels accept the lemma (Rocq Print Assumptions = abstract Section Var only / no Axiom-Admitted; Lean `#print axioms` ⊆ allowlist / no sorry). **MET (§1).**
- [ ] Byte-additive (no emission change) — to verify at implementation; registering an axiom + decls is the established additive pattern (gaps 9–13).
- [ ] os re-proves GREEN (1210 VCs, 7 `#@ \trusted` unchanged) — current `main` is GREEN (gap-16 §4); registration must preserve it.
- [ ] namespace 7/7 + open_existing/fstat/dup still Valid — currently Valid (reproduced §2.2).
- [ ] `content_round_trip` flips — **NOT MET by gap-16 alone; honest next gap = gap-17 (§2.4).** Per the spec mandate ("flips OR the honest next gap"), the gate is satisfied by naming gap-17.

### 4.2 RISKS (led by the two make-or-break questions)

**(a) Does the lemma go through both kernels? — RESOLVED YES.** Rocq `coqc 8.20.1` clean, Print Assumptions = abstract `dat` Section Variable only (no Axiom/Admitted); Lean `4.30.0` clean, axioms `[propext, Quot.sound]` ⊆ allowlist, no sorry. Faithful to the real single-block blit read-after-write (each index set once, same `rd` read-back). The only residual risk is the WhyML transcription: the registry body must state the blit post-state as an explicit antecedent (as written §1.1) so it does NOT over-claim the blit semantics in WhyML — the kernels validate the property GIVEN that antecedent, which is what `sys_write`'s loop invariant supplies.

**(b) THE CRUX — does the reopen size→content link close with a bounded fix? — NO: it is a DEEPER MULTI-GAP ARC.** The §1 byte lemma is the wrong half for the test's `n_read == len(c)` assertion (which is gated by the reopened INODE SIZE via the abstract `dir_lookup`, not by block bytes). Closing it needs (1) a NEW registered name→inode identity lemma `UnixFs.Dir.lookup_after_insert_recovers_inode`, (2) extending/citing the EXISTING `i18.round_trip` to `inode[0]`, and (3) an INODE-KEYED `inode_size`/`inode_content` view threaded through write/close/open/read with a close-frame and create-skip frame. That is gap-17, not a single frame. gap-16's lemma is a prerequisite brick, real progress, but not the keystone for this test.

**(c) Secondary risks.**
- The `content_round_trip` test asserts a COUNT shadow; the TRUE byte equality is additionally not NAMEABLE through count-returning `read` (POSIX `os.read` returns bytes). Even after gap-17 closes the size link, exposing the byte equality needs `read` to return bytes OR expose `content_block` — a test/API-surface decision, flagged, not in this phase.
- `lookup_after_insert_recovers_inode` (gap-17) is expected to cross-validate (finite slot case-split, same shape as `insert_preserves_unique`) but is UNVALIDATED here — its kernel acceptance is the make-or-break of gap-17.
- Registration additivity: must confirm byte-diff identical + corpus/conformance green at implementation (standard gap-9..13 discipline).

---

## 5. Summary

| Item | Status |
|---|---|
| `UnixFs.Content.write_then_read_agree` Rocq proof | ACCEPT (coqc 8.20.1, Print Assumptions = abstract Section Var only, no Axiom/Admitted) — `/tmp/gap16/WriteThenReadAgree.v` |
| `UnixFs.Content.write_then_read_agree` Lean proof | ACCEPT (lean 4.30.0, `#print axioms ⊆ {propext, Quot.sound}`, no sorry) — `/tmp/gap16/WriteThenReadAgree.lean` |
| Lemma faithfulness | concrete single-block blit, each index set once, real read-back; blit post-state an explicit antecedent (not over-claimed) |
| Reopen size→content link | SEVERED by abstract `dir_lookup`; NO inode-size class invariant; `content_round_trip'vc` Postcondition Unknown (reproduced, 312264 steps) |
| Feasibility verdict | gap-16 does NOT close `content_round_trip` — DEEPER MULTI-GAP ARC; next = gap-17 (name→inode identity + inode-keyed size/content view + frames) |
| Registration plan | `UnixFs.Content.write_then_read_agree` in `_AXIOM_REGISTRY`; `content_block` in `_AXIOM_FUNCTIONS` under `UnixFs.Content.`; gap-17 adds `inode_size`/`inode_content` + `lookup_after_insert_recovers_inode` |
| Source edits | NONE (spec phase) |
| Spec status | DRAFT |
