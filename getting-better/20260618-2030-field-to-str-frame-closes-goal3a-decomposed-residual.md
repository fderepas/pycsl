# `_write_dir_entry` goal #3 — `field_to_str_frame` CLOSES goal (3a) + tames (3c); residual decomposed to ONE keystone-value-decode wall + a folded zero/insert maintenance lemma

DATE: 2026-06-18
LOOP: test-supervise-sl (residual goal #3 of `_write_dir_entry` / `_zero_entry`)
STATUS: **NOT retired** (campaign `\trusted` stays 7; net delta 0). But goal **(3a) the
slot_name slot-locality FRAME is SOLVED** with a NEW cross-validated zero-TCB lemma
`field_to_str_frame`, which also TAMES the (3c) explosion (de-trusted `_zero_entry`:
150M-step Type-invariant Timeout → all-fast-Unknown, no Timeout/OOM). The residual is
now PRECISELY decomposed and human-gated. ALL experiments reverted; tree byte-identical
to HEAD (source `git diff HEAD` empty); stash empty.

## Bottom line (the 5 mission questions)
1. **Did `_write_dir_entry` retire (7→6)? NO.** Net `\trusted` delta **0**. Full body
   gate before: **3** goals; after every experiment (reverted): **3** (baseline restored).
2. **Goal (3a) slot_name FRAME — SOLVED** by a NEW Rocq+Lean cross-validated zero-TCB
   lemma `field_to_str_frame`. Goal (3c) explosion — TAMED by the same lemma. Goal (3b)
   invariant maintenance + the keystone VALUE decode — the precise remaining wall.
3. **Precise residual (below):** ONE keystone-value-decode trigger wall (the documented
   ROOT CAUSE #2) that the (3b) maintenance lemmas are DOWNSTREAM of, plus the need to
   keep the byte VALUE term from coexisting with the slot atoms in the invariant VC.
4. **Gating evidence:** `field_to_str_frame` cross-validated Rocq (Closed under global
   context) + Lean (`[propext, Quot.sound]`); corpus-INERT (os `.mlw` byte-identical when
   the registry entry is present but uncited). Tree HEAD-identical; stash empty.
5. **Monitoring update:** new catalog-B row (the field_to_str frame keystone) + the
   decomposed `_zero_entry`/`_write_dir_entry` ledger entry.

## The decisive new result: `field_to_str_frame` (the goal-#2 doc's missing piece)

The 20260618-1640 residual doc said goal (3a) (the slot_name `∀k≠slot` frame) OOMs and
hoped it was "zero-TCB definitional." **That hope is REFUTED at the WhyML level:**
`slot_name`/`slot_inode` are ABSTRACT `val function`s in WhyML (no body to unfold), so the
frame is NOT definitional — it can ONLY come from an emitted byte-keyed axiom. The retired
`block5_decode_frame` requires FULL block-5 byte agreement, which the blit BREAKS (slot's
bytes change). The missing fact is the DISJOINT-region frame:

    field_to_str_frame :
      forall d0 d1 off width [field_to_str d1 off width, field_to_str d0 off width].
        0 <= width ->
        (forall i. 0 <= i < width -> d0[off+i] = d1[off+i]) ->
        field_to_str d0 off width = field_to_str d1 off width

Composed with `slot_name_byte_decode` (slot_name d 5 k = field_to_str d (2560+32*k+2) 30)
this gives the slot_name frame: for k≠slot, slot k's name window is DISJOINT from slot's
32-byte blit window, so the blit's byte frame supplies the antecedent.

**Cross-validated, zero-TCB, BOTH provers (re-confirmed this run, compiled + Print/`#print`):**
- Rocq: `Print Assumptions field_to_str_frame` → **Section Variables only** (`rd0, rd1 :
  Z -> Z`), 0 Axiom/Admitted = **Closed under the global context**. Proof: induction on
  the `scan` fuel (same scan-to-first-null decode as `FieldToStrRoundTrip.v`).
- Lean: `#print axioms field_to_str_frame` → **`[propext, Quot.sound]`** ⊆ allowlist, no
  `sorry`.

## Measured (de-trusted `_zero_entry`, the SIMPLEST mutator — no name string, just zeros;
PYTHONHASHSEED=0, `--fun unixinodefilesystem___zero_entry`)

`_zero_entry` shares the EXACT goal-#3 walls (its contract has the same `∀k≠slot`
slot_inode/slot_name frame ensures + the uniq/slots_lt32 Type-invariant VC) but with NO
string round-trip — so it isolates (3a)/(3b)/(3c) from the goal-#2 complexity.

| config | goals | slot_inode FRAME | slot_name FRAME | Type-inv (uniq/slots_lt32) | slot_inode(slot)=0 |
|---|---|---|---|---|---|
| de-trust, no keystone | 6 | Timeout 922K | OOM | Timeout 91.9M + 2 Unknown | Timeout 12.7M |
| + `slot_inode_byte_decode` | 4 | **Valid 40K** | **OOM** | Timeout 150M + 2 Unknown | Unknown 331K |
| + `field_to_str_frame` (NEW) | 4 | **Valid 43K** | **Valid 42K** ← (3a) SOLVED | **Timeout 2.4M** + 2 Unknown | Unknown 341K |
| + entry_offset = `block_num*512+32*slot` (trigger-align) | **3** | Valid | Valid | **2 fast-Unknown (no Timeout!)** | Unknown 290K |
| + `zero_preserves_uniq/slots_lt32` cited | 3 | Valid | Valid | 2 fast-Unknown | Unknown |

DECISIVE: `field_to_str_frame` turns the slot_name FRAME OOM → Valid (42K steps), AND
collapses the Type-invariant explosion (150M Timeout → fast-Unknown once the offset is
trigger-aligned). The (3c) "the keystone POISONS every mutator's invariant VC" wall is
**substantially defused** — the residual invariant goals are now fast-Unknown (missing
instantiation), not E-match Timeout/OOM.

## The precise REMAINING wall (the human-gated residual)

The 3 surviving `_zero_entry` goals are a CLEAN DEPENDENCY CHAIN, all blocked on ONE root:

1. **ROOT: `slot_inode(self.dir,5,slot) == 0` VALUE postcondition** — `slot_inode_byte_decode`'s
   narrow byte trigger `disk[blk*512+32*k]` needs the literal byte terms `self.dir[entry_offset]`,
   `self.dir[entry_offset+1]` materialized. The body's loop keeps them FOLDED in
   `∀j. self.dir[entry_offset+j]=0` (deliberately — unfolding them re-triggers the
   explosion: a post-loop `#@ assert self.dir[entry_offset]==0` or splitting the two inode
   bytes out of the loop both REGRESS to 22-28M Timeout). This is the documented
   ROOT CAUSE #2 (20260617-1240) — the byte VALUE term and the slot atoms cannot coexist
   in one VC.
2. **`uniq(self.dir)` Type-invariant** — `zero_preserves_uniq` (already cross-validated +
   now cited) needs `slot_inode d1 5 slot = 0` as its antecedent → DOWNSTREAM of (1).
3. **`slots_lt32(self.dir)` Type-invariant** — `zero_preserves_slots_lt32` likewise
   DOWNSTREAM of (1).

So goal (3b) is NOT a missing lemma (the maintenance lemmas exist, are cross-validated, and
were emitted on citation) — it is starved of its `slot_inode(slot)=0` antecedent by the
ROOT keystone-value wall.

## The EXACT human-gated lemma to finish (doctrine option (b), TCB decision)

A single FOLDED `zero_preserves_dir_invariant` (the gap-17/`block_content_eq` discipline)
keyed so NO byte term coexists with a slot atom in the caller VC: take the two zeroed inode
BYTES + the byte-region frame as a folded byte-side hypothesis, conclude
`slot_inode d1 5 slot = 0  ∧  (∀k≠slot. slot decode equal)  ∧  uniq d1  ∧  slots_lt32 d1` in
ONE step. The byte→inode==0 rung (the keystone) and the abstract-slot invariant rung are
then discharged INSIDE the lemma (offline, Rocq+Lean), never sharing a goal in the body VC.
This is structurally the `remove_unique_absent`/`insert_preserves_*` family EXTENDED with the
byte rung folded away — a NEW cross-validated axiom. Authoring + adopting it is a
**human-gated TCB decision**; the loop may not adopt it autonomously.

The write-side (`_write_dir_entry`) additionally needs the goal-#2 `slot_name` VALUE
postcondition (already CLOSED at the method level via `#@ sibling_concrete`, 20260618-1640)
AND the same folded INSERT-side invariant lemma. `field_to_str_frame` (this doc) is the
shared (3a) substrate both need; it is the BANKED rung-1 of the eventual retirement.

## `field_to_str_frame` is the proposed first emission (corpus-inert, cross-validated)

`field_to_str_frame` ALONE is independently safe to land (it strengthens nothing on its own;
emission-gated by `#@ proof` citation; os `.mlw` byte-identical when present-but-uncited —
verified this run). It does not by itself retire any trust, but it is the foundation goal
(3a) was blocked on, and it removes the OOM/Timeout class from every dir-mutator frame VC.
Recommend the human:
1. Add the cross-validated `field_to_str_frame` proof to
   `test-suite/corpus/pycsl-reference/0708.proofs/{rocq,lean}/` (alongside FieldToStrRoundTrip)
   or a new `FieldToStrFrame.{v,lean}` (the probe compiled clean both provers — see below).
2. Add the registry entry to `_AXIOM_REGISTRY` (the exact WhyML form above) with the
   doc-coherency surfaces updated.
3. Author the folded `zero_preserves_dir_invariant` / `insert_preserves_dir_invariant`
   (byte rung folded) and cross-validate before any de-trust.

## Cross-validation re-confirmed this run (compiled + assumptions shown)
- `field_to_str_frame` (NEW probe, /tmp, now cleaned): Rocq Section-Variables-only; Lean
  `[propext, Quot.sound]`.
- `0708.proofs/rocq/FieldToStrRoundTrip.v`: coqc clean.
- `DirInvariantMaintenance.v` `Print Assumptions` (added temporarily to a /tmp copy): all four
  of `zero_preserves_uniq`, `zero_preserves_slots_lt32`, `insert_preserves_uniq_folded`,
  `insert_preserves_slots_lt32` → **Closed under the global context** (Section Variables only).
- `Block5DecodeFrame.v`: coqc clean (full-block frame — superseded for the mutator case by
  the disjoint-region `field_to_str_frame`).

## Gating evidence
- Source `git diff HEAD` empty (src/, pure_lib/, *.py, *.md, proofs); stash empty.
- `field_to_str_frame` registry entry present-but-uncited → os module `.mlw` BYTE-IDENTICAL
  to baseline (corpus-inert; the doctrine's emission-gated property holds).
- Baseline full body gate re-confirmed **3 goals** (`_unpack_direntry`×2 Precondition Unknown
  320K/337K; `sys_rename` Assertion Timeout 4.6M — the documented aggregate noise).
- All Rocq/Lean compile artifacts + /tmp probes removed; tree restored.
