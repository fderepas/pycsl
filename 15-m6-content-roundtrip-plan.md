# M6 — content round-trip (sys_write fidelity → cross-call read recovery)

> **STATUS 2026-06-15 (autonomous run).** Phase 0 ✅, Phase 1 ✅ (**sys_write 40 → 0**),
> Phase 3 ✅ (`sys_pread` + `os.pread`), **gap-17 ✅ SOLVED** (commit 9e71e5d): the content
> round-trip is closed through the public API via the FOLDED `block_content_eq` predicate
> (definitional intro/elim) — it crosses no_inline where the ∀i / `\array_eq` could not
> (slice-in-`\array_eq` was a red herring: `\array_eq` IS the ∀i). Pieces: sys_write ⟹
> block_content_eq (379/0); sys_pread ⟹ block_content_eq (36/0); wrappers propagate the
> atoms (__init__ GREEN 1128/0); `_content_compose` (26/0): two atoms ⟹ `\array_eq` (back==c).
> Corpus byte-diff clean 601/601. Phase 2 (multi-block content) = loop content-∀i divergence;
> a single create→write→read function (formal_0008) = orthogonal PyCSL harness bugs
> (bool-return, assert-in-if, slot_inode decl for importer tests). Commits a998516, dd88e23,
> 9e71e5d.


Status entering M6 (body gate, branch `m6-content-roundtrip` off `main` @ 61f1afc):
every `os` directory syscall + helper is **0** except **sys_rename (3, proven
SMT-divergent — parked)** and **sys_write (40)**. M6 closes the last functional
property: a file's bytes survive `write` and come back out of `read`/`pread`.

## 1. What's already proven (the foundation)

- **`_block_roundtrip` is CLEAN (47/0).** It does exactly the core content move —
  `self.disk[start:start+n] = data` (→ `Array.blit`) then reads the slice back
  (`Array.sub`) and proves `\array_eq(\result, data)` with `data` UNIVERSALLY
  quantified, AND maintains the class invariants (`inode_bytes_valid(self.disk)`,
  directory `[2560,3072)` preservation). So the blit per-element fidelity + the
  byte-range class-invariant maintenance after a data-block write are NOT the wall.
- **gap-16 content view is already wired into sys_write's contract:** the on-disk
  content view of a file is the disk slice `self.disk[fd_block[fd]*512 + i]`; the
  two content ensures (single-block completion + `\forall i. disk[...+i]==data[i]`)
  are already written. The 40 residual are proving them through the multi-block loop.

## 2. The actual gap (sys_write's 40)

sys_write differs from the proven `_block_roundtrip` leaf by the INTEGRATION around
the blit:
1. the **multi-block loop** (block_idx 0..9, `_alloc_block` on demand) — the two
   content ensures + the loop invariants must compose ACROSS iterations;
2. **block-position reasoning** — the byte-range frame for `inode_bytes_valid`
   needs `p_block*512 >= 2560` (data blocks live above the inode region), i.e.
   `p_block >= 6`, derived from `_alloc_block`'s post / the inode block field;
3. **single-block completion** — `result == len(data)` (the loop runs exactly once
   when offset 0 ∧ n ≤ 512) unless `_alloc_block` fails;
4. the **∀i content fidelity** carried as a loop invariant across the blit + frame.

(Full per-goal breakdown TODO: the `--fun unixinodefilesystem__sys_write` measurement
is itself billion-step slow; Phase 0 gets a faster signal via the single-block path.)

## 3. Plan (leaf-first, measure each step; gates every step)

### Phase 0 — de-risk / measure (fast signal)
- Get the real goal breakdown WITHOUT the slow full multi-block proof: prove the
  **single-block path** in isolation (offset 0, n ≤ 512 ⇒ the loop runs once). Two
  routes: (a) a `requires \length(data) <= 512` scoped measurement, or (b) extract
  the loop body into a `_write_block` leaf and prove it standalone.
- Decide which sub-problem dominates: the loop composition vs the completion vs the
  `p_block >= 6` byte-range frame. Pick the leaf order from the data.

### Phase 1 — write-side, SINGLE block (the round-trip scenario)
- Close sys_write's two content ensures for `offset 0 ∧ n ≤ 512` (the `formal_0008`
  scenario). Leverage the `_block_roundtrip` pattern: likely extract
  **`_write_block(p_block, block_off, data, written, chunk)`** — one blit, ensures
  `\forall j. 0<=j<chunk ==> disk[p_block*512+block_off+j] == data[written+j]` +
  the byte-range/uniq frame + `p_block >= 6 ==> ...`. Prove it as a clean leaf
  (cf. `_block_roundtrip`), then the single-iteration loop composes it.
- Target: single-block sys_write content fidelity + completion → 0.

### Phase 2 — write-side, MULTI block
- Generalize the loop invariant to blocks 0..9: the ∀i fidelity over a per-block
  union (each block contributes `[block_idx*512, +chunk)`). Watch the quantifier
  cost — if it diverges (cf. rename), a narrow per-block-frame lemma (cross-validated,
  like the dir lemmas) carries the prefix as a scalar across each blit.

### Phase 3 — cross-call read recovery (gap-17, the load-bearing piece)
- Today `sys_read`/`pread` return a COUNT, not content; there is NO content-returning
  read. Add a **content-returning `pread`** (or expose the resolved data block) so a
  caller can connect `write`'s content effect to `read`'s output across calls — the
  gap-17 cross-call EFFECT contract. This is the genuinely new modeling (the abstract
  intervening calls must not havoc the data block; the resolved-block must be exposed).

### Phase 4 — compose acceptance + gates
- `formal_0008.py` (the content round-trip, `\result == True`) proves end-to-end.
- Gates EVERY step: os `__init__` GREEN; corpus byte-diff (`bin/byte-diff-sweep.sh`)
  clean; faithful (no totalization, no value→int); any new axiom DERIVED (zero-TCB)
  or cross-validated Rocq+Lean. Add a reference-corpus entry for the content property.

## 4. Risks
- **Quantifier cost** of the multi-block ∀i (Phase 2) — same risk class as the rename
  divergence; mitigate with a cross-validated per-block-frame lemma + scalar carry.
- **gap-17 cross-call framing** (Phase 3) is the real research: intervening abstract
  calls between write and read; exposing the resolved block soundly without an
  over-strong assumption. This is the multi-session core (per os-coverage memory).
- **`_alloc_block` post** must give `result >= 6` (data block above inode region) for
  the byte-range frame; verify/strengthen its contract first if it doesn't.
