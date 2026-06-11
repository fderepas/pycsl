STATUS: DONE

<!-- IMPLEMENTATION (gap-13 CLOSED — uniqueness PROVEN, out of the TCB):
- 2 axioms registered in _AXIOM_REGISTRY (module6_whyml/preamble.py):
  UnixFs.Dir.empty_disk_slots_dead (Wall E) + UnixFs.Dir.block5_decode_frame (Wall M).
  Proofs shipped to unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/
  EmptyDiskSlotsDead.{v,lean} + Block5DecodeFrame.{v,lean}. BOTH kernels accept BOTH:
  Rocq coqc exit 0, Print Assumptions = Section Variables only (Closed, 0 Axiom/Admitted);
  Lean exit 0, #print axioms = [propext, Quot.sound] ⊆ allowlist. axiom-registry.md 4→6.
- Helper frames: block-5 decode-frame ensures on _write_inode/_alloc_inode/_alloc_block/
  _block_roundtrip + decode-frame ensures + write-locality requires (byte_offset+bit//8 < 2560)
  on _set_bitmap; each proves its byte-frame from its disjoint blit/single-byte write.
- Class invariant ACTIVATED on UnixInodeFileSystem; establishment discharges via
  empty_disk_slots_dead (Wall E vacuous on the zeroed Array.make).
- _dir_find_slot trusted UNIQUENESS ensures REMOVED — uniqueness now FOLLOWS from the
  active class invariant (the two decode-fidelity ensures stay legitimately trusted).
- R4 (real VCs): the maintenance balloon at the INLINED non-directory syscalls
  (chmod/chown/utimensat/truncate/ftruncate) was TUNED with body byte-frame + decode-frame
  #@ asserts (citing block5_decode_frame); truncate/ftruncate additionally pin the disjointness
  bound (512+inode*64+64 <= 2560) to avoid an Alt-Ergo/Z3 OOM on the 4294967295-bounded
  field-0 pack. NO re-trust, NO fake. The no_inline syscalls (open/write) carry the maintenance
  as assumed val contracts (existing model). TOOL: ir_resolve._strip_dir_scan_proofs keeps the
  2 gap-13 axioms past the importer strip; Module6 hoists the class-inv axioms+decls BEFORE the
  record (Why3 axiom-scope-from-declaration-onward — the establishment fix); 
  _precompute_axiom_logic_funcs now also walks class invariants so an importer that inherits the
  invariant but cites no Dir axiom (formal_os_namespace) binds slot_inode (not slot_inode_3).
- GATES: os GREEN (see VC count in final report); 7/7 formal_os_namespace consequences VALID via
  standard pipeline; full-corpus byte-diff IDENTICAL (595 files); conformance 38/38; doc green. -->


<!-- COORDINATION APPROVAL (editorial):
- BOTH AXIOMS APPROVED (dual-kernel accepted, faithful): `UnixFs.Dir.empty_disk_slots_dead` (a zeroed
  block-5 region decodes to all-dead slots — reflects the real 2-byte BE decode of zero bytes) and
  `UnixFs.Dir.block5_decode_frame` (decode-locality: disks agreeing on block-5 bytes [2560,3072) have equal
  block-5 decode — same dirscan-fidelity trust class as _write_entry's slot-locality frame).
- PLAN APPROVED (bounded, CLOSES — not a grind): register the 2 axioms; add the block-5-decode-frame
  `ensures` to the ~5 disk-writing helpers (_write_inode, _set_bitmap, _alloc_inode, _alloc_block,
  _block_roundtrip) + the write-locality `requires` on _set_bitmap; the 7 non-directory syscalls
  (chmod/chown/utimensat/write/truncate/ftruncate/open) delegate to those helpers and get the obligation for
  free; then ACTIVATE the uniqueness class invariant (establishment via empty_disk_slots_dead) and DROP the
  trusted `_dir_find_slot` uniqueness ensures.
- MANDATORY (R4): the PoC modeled helpers as opaque vals — the IMPLEMENT phase MUST re-run the REAL os VCs
  (actual bodies + real invariant lowering). If a real VC trigger-differs, tune (assert/no_inline) — do NOT
  re-trust, do NOT fake. Keep os GREEN at every stage.
THE GOAL: uniqueness PROVEN — the `\trusted` uniqueness ensures on `_dir_find_slot` REMOVED.
Acceptance bar: both kernels accept both axioms; os re-proves GREEN; the 7/7 formal_os_namespace
consequences STILL VALID (standard pipeline); the trusted uniqueness ensures REMOVED; full-corpus byte-diff
IDENTICAL; conformance 38/38; doc green. Set STATUS: DONE on success (uniqueness proven), else
IMPLEMENTED-PARTIAL with the honest state + a follow-on gap. -->

<!--
(orig) STATUS: DRAFT — TOOL-AGENT (SPEC PHASE) output for gap-13.
Validates the two activation axioms for the directory-uniqueness CLASS
INVARIANT and assesses the make-or-break BREADTH of Wall M. NO source edits;
proofs validated in /tmp under both kernels. Companion to
11-1404-convergence-gap-13.md.
-->

# Spec-13 — discharge the directory-uniqueness class invariant (Wall E + Wall M)

STATUS: DRAFT

## 0. Goal (from the user, unchanged)

Make directory uniqueness a PROVEN, maintained class invariant on
`UnixInodeFileSystem` (`pure_lib/os/UnixInodeFileSystem.py`) and DROP the
`\trusted` uniqueness ensures on `_dir_find_slot`. gap-12 made the invariant
STATABLE (Wall A tool fix) and proved the 7 directory mutators' insert-side
maintenance under the registered `UnixFs.Dir.insert_preserves_unique`.
Activation then walled on two discharge gaps: **Wall E** (vacuous establishment
on the zeroed disk) and **Wall M** (maintenance obligation on EVERY
`assigns self.disk` method, not just the 7 directory mutators). This spec
validates the two axioms those walls need and reports a feasibility verdict.

## 1. Wall E — the empty-disk-decode axiom (VALIDATED, both kernels)

### 1.1 Statement (registry form, over the existing abstract symbols)

```
UnixFs.Dir.empty_disk_slots_dead:
  forall disk: array int. forall blk: int.
    ( forall b: int. blk*512 <= b < blk*512 + 512 -> disk[b] = 0 ) ->
    ( forall k: int. 0 <= k < 16 -> slot_inode disk blk k = 0 )
```

Faithful: `slot_inode (disk, blk, k)` is the 2-byte big-endian decode of the
inode field of slot k's 32-byte dirent (`256*disk[off] + disk[off+1]`,
`off = blk*512 + 32*k`). A zeroed dirent region yields inode field 0 — this is
the property of `_unpack_direntry` / `_unpack_uint16_be` of all-zero bytes, not
an over-claim. It is the ANTECEDENT-discharge dual of `slot_inode_nonneg`: it
makes the constructor's `Array.make 131072 0` witness establish the invariant
VACUOUSLY (all 16 block-5 slots dead → no live duplicate pair).

### 1.2 Kernel evidence (proofs in /tmp, runnable; ship to the proofs tree)

- **Rocq 8.20.1** (`/tmp/gap13/EmptyDiskSlotsDead.v`): `coqc` exit 0;
  `Print Assumptions` = **Closed** under the global context (only the two
  abstract Section Variables `disk : Type`, `rd : disk -> Z -> Z`). No Axiom, no
  Admitted. `slot_inode` is DEFINED as the concrete decode over `rd`; the proof
  rewrites the two field bytes to 0 under the region-zero hypothesis and closes
  by `lia`.
- **Lean 4.30.0** (`/tmp/gap13/EmptyDiskSlotsDead.lean`, core only, no Mathlib):
  exit 0; `#print axioms` = `[propext, Quot.sound]` ⊆ allowlist. No `sorry`.

VERDICT (Wall E): **CLOSES.** The axiom goes through both kernels and is
faithful. With it registered in `_AXIOM_REGISTRY` under `UnixFs.Dir.*` (no new
`_AXIOM_FUNCTIONS` entry — it reuses `slot_inode`), the establishment VCs
(`unixinodefilesystem'vc` type-invariant witness, `_filesystem'vc`
precondition) become vacuous. Wall E is a bounded, one-axiom fix.

## 2. Wall M — the block-5-decode frame + BREADTH assessment

### 2.1 The frame axiom (VALIDATED, both kernels)

```
UnixFs.Dir.block5_decode_frame:
  forall d0 d1: array int.
    ( forall b: int. 2560 <= b < 3072 -> d0[b] = d1[b] ) ->
    ( forall k: int. 0 <= k < 16 ->
        slot_inode d1 5 k = slot_inode d0 5 k /\
        slot_name  d1 5 k = slot_name  d0 5 k )
```

DECODE-LOCALITY: `slot_inode`/`slot_name (disk, 5, k)` read ONLY the 32 bytes of
slot k's dirent, all inside block 5's region `[2560, 3072)`. Two disks agreeing
on `[2560,3072)` therefore have identical block-5 decode at every slot. Same
byte-local-decode trust class as `_write_entry`/`_zero_entry`'s existing
slot-locality frames and as `empty_disk_slots_dead`.

- **Rocq 8.20.1** (`/tmp/gap13/Block5DecodeFrame.v`): `coqc` exit 0;
  `Print Assumptions` = Section Variables only (`byte_disk`, `rd`, `name_t`,
  `name_decode`); no Axiom/Admitted. `slot_inode` is the big-endian decode;
  `slot_name` is `name_decode` applied to the 30 explicit name bytes; the proof
  rewrites every read under the byte-agreement window (no funext, no induction).
- **Lean 4.30.0** (`/tmp/gap13/Block5DecodeFrame.lean`, core only): exit 0;
  `#print axioms` = `[propext, Quot.sound]` ⊆ allowlist. No `sorry`.

### 2.2 Proof-of-concept: does chmod's invariant-preservation discharge WITH the frame? — YES

Modelled the chmod scenario in Why3 (1.8.2, Z3 4.13.3), `split_vc`:

- **Without any frame** (`/tmp/gap13/wallm.mlw`): the inode write (region
  `[512, 2560)`) re-establishing `uniq` over uninterpreted `slot_inode` →
  **Timeout (5s, 3.7M steps)**. Reproduces the gap-13 chmod timeout.
- **With the full chain** (`/tmp/gap13/wallm_chain.mlw`): `_write_inode` modelled
  as an opaque `val` carrying a block-5-BYTE-frame ensures
  (`forall c. 2560<=c<3072 -> disk[c] = old disk[c]`), the
  `block5_decode_frame` axiom registered, and a ONE-LINE decode-locality
  instantiation assert in chmod → `ensures { uniq d }` is **Valid (0.01s, 10656
  steps)**. No timeout.
- **Best shape — DECODE-frame hoisted into the helper ensures**
  (`/tmp/gap13/wallm_decframe.mlw`): if `_write_inode`'s ensures states the
  DECODE frame directly
  (`forall k. 0<=k<16 -> slot_inode(self.disk,5,k) == \old(slot_inode(self.disk,5,k)) /\ slot_name(...)==\old(...)`),
  then chmod AND chown discharge `ensures uniq` with **ZERO annotation in the
  syscall body** (Valid, ~8.2k steps each).
- **Helper body proves its own decode-frame ensures**
  (`/tmp/gap13/wallm_helperbody.mlw`): `_write_inode`'s body (`Array.blit` into
  `[off, off+64) ⊆ [512,2560)`) proves the byte-frame from the blit (pure array
  reasoning), the registered `block5_decode_frame` converts byte→decode, and the
  decode-frame ensures discharges (Valid, ~15.5k steps).

So the chain is mechanically verified end-to-end: blit → byte-frame →
(registered axiom) → decode-frame ensures on the helper → free `uniq`
maintenance at every syscall that writes only through that helper.

### 2.3 BREADTH — how many writers need the frame?

There are **23 distinct methods with `assigns self.disk`**:

| Class | Methods | Frame burden |
|---|---|---|
| **Block-5 dirent writers** (the frame does NOT apply — they ARE the mutation) | `_write_entry`, `_zero_entry`, `_write_directory`, `_format_disk` | already carry insert/remove slot-locality; maintenance via `insert_preserves_unique` (gap-12) |
| **7 directory mutators** | `sys_mkdir`, `sys_rmdir`, `sys_link`, `sys_unlink`, `sys_rename`, `sys_symlink`, `sys_creat` | already proved insert-side under gap-12 citations |
| **Non-block-5 disk-writing HELPERS** (need a decode-frame ensures) | `_write_inode`, `_set_bitmap`, `_alloc_inode`, `_alloc_block`, `_block_roundtrip` | **5 helpers** — the actual frame surface |
| **Non-directory SYSCALLS** (delegate to the helpers) | `sys_chmod`, `sys_chown`, `sys_utimensat`, `sys_write`, `sys_truncate`, `sys_ftruncate`, `sys_open` | **0 annotation IF the helpers carry the decode-frame ensures** (POC §2.2) |

The frame is therefore **NOT per-syscall**: it lives on the ~5 helpers. If the
decode-frame ensures is hoisted onto each helper, every non-directory syscall
inherits `uniq` maintenance for free (PoC: chmod + chown, zero body
annotation). The registered `block5_decode_frame` axiom is written ONCE.

Per-helper provability of the byte-frame (the only real work):

- `_write_inode` — blit `[512+inode*64, +64) ⊆ [512,2560)`, disjoint from block 5
  → byte-frame **trivial** (PoC §2.2 confirms Valid).
- `_block_roundtrip` — writes data block `block` with `block>=6` (bytes
  `>=3072`), disjoint → byte-frame trivial.
- `_alloc_inode`/`_alloc_block` — write the bitmap blocks (bytes ~512..1535),
  disjoint → byte-frame trivial.
- `_set_bitmap` — writes `byte_offset + bit_index//8`; needs a write-locality
  PRECONDITION (`byte_pos < 2560` or `>= 3072`) to prove disjointness. All call
  sites pass the system-block bitmap offsets (block 4 / inode-data bitmaps), so
  the precondition holds, but this is the one helper whose frame needs a small
  requires.

### 2.4 FEASIBILITY VERDICT — Wall M CLOSES (bounded), it does NOT grind

The make-or-break fear was an N-syscalls × E-matching blowup. The PoC refutes
it: the obligation is discharged at the ~5 HELPERS, not the ~13
directory-and-non-directory syscalls, and the discharge is a ~10–16k-step
rewrite (sub-second), NOT a 232M-step balloon. The class-invariant path is a
BOUNDED fix:

1. register `empty_disk_slots_dead` (Wall E) — 1 axiom;
2. register `block5_decode_frame` (Wall M) — 1 axiom;
3. add a decode-frame `#@ ensures` to the 5 non-block-5 disk-writing helpers
   (`_write_inode`, `_set_bitmap`, `_alloc_inode`, `_alloc_block`,
   `_block_roundtrip`), each provable from its blit/byte-write disjointness
   (one `#@ assert` byte-frame inside the helper body), plus a write-locality
   `#@ requires` on `_set_bitmap`;
4. re-activate the class invariant; drop the `_dir_find_slot` trusted uniqueness
   ensures.

No open-ended grind: the E-matching is local to each helper VC (one disk pair,
one quantified k over `[0,16)`), Z3 instantiates the registered axiom on the
explicit byte-agreement, and it composes because syscalls never re-derive the
invariant directly — they inherit it through the helper's decode-frame ensures.

## 3. Local-lemma alternative (NOT needed — recorded for completeness)

Because Wall M closes, the lower-cost alternative (proving uniqueness as a LOCAL
lemma threaded only through the 7 directory ops, NOT a global Why3 class
invariant) is NOT required. It would avoid obligating the non-directory writers
entirely (no helper frames), but it would NOT be a class invariant — it would be
a per-directory-op postcondition the caller must thread, which is weaker (it is
not automatically available as a precondition to every method) and changes the
user's stated "class invariant" choice. RECOMMENDATION: keep the class-invariant
choice; the bounded §2.4 plan delivers it. (Flagging the alternative only so the
user knows the cheaper fallback exists if the §2.4 helper-frame work surprises.)

## 4. Gate (for the IMPLEMENT phase that follows this spec)

- byte-additive: the two new axioms are gated by `_class_inv_refs_axiom_func`
  (False for the rest of the corpus); helper-frame ensures only emit on os →
  full-corpus byte-diff must stay IDENTICAL outside os.
- os GREEN: 0 unproven goals after activation (the 3 walls' VCs — VC1/VC2
  establishment, VC3 chmod, and the analogous chown/utimensat/write/truncate/
  open type-invariant VCs — all Valid).
- 7/7 `formal_os_namespace.py` namespace consequences still VALID.
- conformance 38/38; doc-coherency green; axiom-registry.md `UnixFs.Dir.*`
  count 4 → 6 (+ empty_disk_slots_dead, + block5_decode_frame).
- uniqueness PROVEN: `_dir_find_slot` trusted uniqueness ensures DROPPED.

## 5. RISKS

- **R1 (low):** `_set_bitmap`'s write-locality `#@ requires` must hold at every
  call site; if any caller passes an offset that could land in `[2560,3072)`,
  the frame breaks. Mitigation: all current callers use system-block bitmap
  offsets (block 4 / inode-data); verify at IMPLEMENT, byte-check.
- **R2 (low):** the decode-frame ensures on a helper must itself be PROVABLE
  from the body (byte-frame from the blit). PoC confirms for `_write_inode`;
  `_block_roundtrip`/`_alloc_*`/`_set_bitmap` are the same blit/single-byte
  shape but each needs its own `#@ assert` byte-frame — verify each at IMPLEMENT
  (cheap, but it IS per-helper work, not zero).
- **R3 (low):** the two new axioms reuse the registered `slot_inode`/`slot_name`
  symbols; confirm no `_AXIOM_FUNCTIONS` drift and that the importer (os
  `__init__.py` wrappers) does not pull the heavy frame axiom into wrapper VCs
  (gate keeps it os-local).
- **R4 (medium-residual):** the PoC modelled helpers as opaque `val`s with the
  proposed ensures; the REAL helper bodies + the REAL invariant lowering may
  surface trigger differences. The chmod VC is the canonical worst case and it
  discharged in 10–16k steps with margin, so the risk is small, but the
  IMPLEMENT phase must re-run the actual os VCs (not just the /tmp models).

## 6. Artifacts (validated, in /tmp/gap13/ — ship to the proofs tree at IMPLEMENT)

- `EmptyDiskSlotsDead.v` / `.lean` — Wall E axiom (both ACCEPT).
- `Block5DecodeFrame.v` / `.lean` — Wall M frame axiom (both ACCEPT).
- `wallm.mlw` (no-frame timeout), `wallm_chain.mlw` (full chain Valid),
  `wallm_decframe.mlw` (hoisted-ensures, zero syscall annotation, Valid),
  `wallm_helperbody.mlw` (helper body proves its own frame, Valid) — Why3 PoCs.
