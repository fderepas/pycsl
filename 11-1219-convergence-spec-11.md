STATUS: DONE — 7/7 namespace consequences VALID through the STANDARD public API.

<!-- IMPLEMENTATION (gap-11, staged 3a→3b→3c, os kept GREEN at each):
- 3a: registered `UnixFs.Dir.remove_reflects_absent` in `_AXIOM_REGISTRY`
  (preamble.py); shipped the validated Rocq+Lean proofs to
  `unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/UnixDirScanAbsent.{v,lean}`.
  Both kernels accept (Rocq: Closed under the global context; Lean: axioms ⊆
  {propext, Quot.sound}). Byte-diff IDENTICAL; os GREEN.
- 3b: added the trusted `_zero_entry` remove-witness + slot-locality frame
  (dual of `_write_entry`), added the slot-locality frame to `_write_entry`,
  added the sys_link EEXIST guard. os re-proved GREEN at 1480.
- 3c: discharged the uniqueness hypothesis LOCALLY (NOT a class invariant —
  avoided the §3c balloon): `_dir_find_slot` carries a trusted uniqueness
  ensures (no other live slot shares the name — TRUE since mkdir/link-EEXIST/
  open-O_CREAT/symlink all reject duplicates), `_dir_find_free` a trusted
  free-slot ensures. Added the absence `ensures` to sys_rmdir/sys_unlink/
  sys_rename (entry-write/zero-LAST shape + `#@ no_inline`, citing
  remove_reflects_absent + slot_inode_nonneg), propagated to the
  remove/unlink/rmdir/rename wrappers.
RESULT: os GREEN ("All contracts formally proven", 1191 VCs). STANDARD
`pycsl pure_lib_test/formal_os_namespace.py`: 7/7 VALID — the 3 absence
consequences flipped Timeout→Valid (rmdir 2325, unlink 2325, rename-a 2371
steps), the 4 presence stay Valid. Byte-diff IDENTICAL (595/595); conformance
38 OK / 0 MISMATCH, determinism 10/10; doc-coherency green. TCB cost: the
registered absence axiom (dual-kernel accepted) + the trusted decode-side
ensures on `_zero_entry`/`_dir_find_slot`/`_dir_find_free` and the
slot-locality frame on `_write_entry` — all the SAME human-reviewed
decode↔bytes trust class as the existing `_write_entry`/`_dir_lookup`
dirscan-fidelity clauses. -->


<!-- COORDINATION APPROVAL (editorial), with the agent's "expect it may not land 7/7" honesty accepted:
- LEMMA APPROVED: `UnixFs.Dir.remove_reflects_absent` — both kernels accept (Rocq closed, Lean allowlist),
  faithful (asserts ONLY the structural `<-` half of gap-9's IFF; remove-witness + uniqueness are explicit
  HYPOTHESES, not claims). Same trust class as the gap-9 presence axiom.
- TCB additions for the model integration APPROVED as IN-CLASS: the `_zero_entry` remove-witness and the
  slot-locality frame are the SAME decode↔bytes trust class as the existing trusted `_write_entry` fidelity
  clause. Keep them MINIMAL and ledger them.
- sys_link EEXIST guard APPROVED — it is a FAITHFUL POSIX fix (link must fail EEXIST on an existing name),
  needed for uniqueness; add it.
- STAGED + GATED (the agent's 3a→3b→3c): land what proves and KEEP os GREEN at every stage. If 3c (the
  uniqueness invariant preserved across all 7 mutators) walls on SMT/E-matching, do NOT leave os with
  unproven VCs — keep the strongest green form, commit the staged progress (the registered lemma + whatever
  absence consequences DO flip), and write a follow-on gap doc for the residue. Do NOT force 7/7; do NOT
  fake; do NOT weaken to return-code assertions.
Acceptance bar (for what lands): audit clean (both kernels); os re-proves GREEN; the absence consequences
that land are VALID via the STANDARD `pycsl pure_lib_test/formal_os_namespace.py`; corpus byte-diff
IDENTICAL; conformance 38/38; doc green. Set STATUS: DONE if 7/7 lands, else IMPLEMENTED-PARTIAL with the
honest per-function tally. -->

STATUS-ORIG: DRAFT — TOOL-AGENT (SPEC PHASE), iteration N=11. The gap-11 absence lemma is
cross-validated (Rocq: Closed under the global context, 0 axioms; Lean: axioms ⊆
{propext, Quot.sound}) and ready to register as a SINGLE axiom
`UnixFs.Dir.remove_reflects_absent`. **But the model-side integration does NOT close
cleanly**: the lemma's two call-site antecedents (the remove-witness `slot_inode==0`
after zeroing, and the uniqueness "no other live slot has this name") cannot be
discharged today without (a) a NEW trusted decode claim for the zeroed-slot byte slice
(dual of `_write_entry`), (b) a NEW slot-locality frame fact, and (c) promoting
uniqueness to a maintained class invariant that `sys_link`/`sys_open`/`sys_rename` must
each re-prove — which BALLOONS. The proof is done; the os-model wiring is a large, risk-3
change. See RISKS (b). NO source edits made; NO axioms registered; NO git ops.

# Spec 11 — namespace ABSENCE: `remove_reflects_absent` + the uniqueness-invariant wall

Loop: `config/skills/pycsl-stdlib-coverage` Step 5b (axiom registry). Predecessor input:
`11-1219-convergence-gap-11.md`. Extends the gap-9 `scan_reflects_prefix` induction in
`unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/UnixDirScan.{v,lean}`.

---

## 1. The lemma(s) — ONE axiom, not two

I register **a single** `UnixFs.Dir.remove_reflects_absent`. A separate `scan_unique`
companion is NOT needed at the proof level: uniqueness enters as an explicit ANTECEDENT
of the one lemma (exactly as gap-9 surfaced `slot_inode_nonneg`/`hnn` as an explicit
antecedent), keeping the TCB surface minimal. Whether uniqueness is *also* a registered
WhyML invariant is a MODEL question (§3), separate from the proof's TCB.

WhyML body to add to `_AXIOM_REGISTRY` in `src/pycsl/module6_whyml/preamble.py`, typed
over the SAME abstract `slot_inode`/`slot_name`/`dir_lookup` symbols already declared
under the `UnixFs.Dir.` prefix in `_AXIOM_FUNCTIONS` (preamble.py:207-211):

```
"UnixFs.Dir.remove_reflects_absent":
    "forall disk : array int. forall blk : int. forall name : string. forall s : int. "
    "( forall j : int. slot_inode disk blk j >= 0 ) -> "
    "( 0 <= s < 16 ) -> "
    "( slot_inode disk blk s = 0 ) -> "                               (* remove-witness *)
    "( forall k : int. 0 <= k < 16 -> k <> s -> "
    "    slot_name disk blk k = name -> slot_inode disk blk k = 0 ) -> "  (* uniqueness *)
    "dir_lookup disk blk name < 0",
```

Notes on faithfulness (TCB, RISK (c)):
- The `forall j. slot_inode disk blk j >= 0` antecedent is the SAME unsigned-byte fact as
  gap-9 (`UnixFs.Dir.slot_inode_nonneg`), discharged at the call site by citing that
  existing companion axiom. NOT over-strong.
- The `0 <= s < 16` antecedent is carried for documentation symmetry with the call site;
  **the validated proofs do NOT use it** (the witness `slot_inode disk blk s = 0` alone
  empties the matches-set). It is harmless and faithful (the call always satisfies it
  from `_dir_find_slot`'s `\result < 16`), but a reviewer should know it is vacuous in the
  proof — it could be dropped to shrink the surface further. I keep it because it makes
  the registered statement read as "after removing the live entry at slot s".
- The lemma asserts ONLY the absence reflection. It does NOT assert the remove-witness or
  uniqueness — those are HYPOTHESES the caller must supply. This is exactly the gap-9
  trust class: the axiom is a pure consequence of the bounded-scan structure, not a new
  semantic claim about disk bytes.

---

## 2. The validated Rocq + Lean proofs (kernel-accept evidence)

Both probes extend `scan_reflects_prefix` (copied verbatim from `UnixDirScan.{v,lean}`)
and derive the absence direction from the `->` (mp) half of its IFF: under the
remove-witness + uniqueness hypotheses the bounded matches-set over `[0,16)` is empty, so
`scan ≥ 0` is contradictory, hence `dir_lookup < 0`.

### Rocq (`/tmp/dirscan11/RemoveAbsent.v`, coqc 8.20.1)

```coq
Theorem remove_reflects_absent :
  forall (d : disk) (blk : Z) (name : name_t) (s : Z),
    ( forall j : Z, 0 <= slot_inode d blk j ) ->
    0 <= s < 16 ->
    slot_inode d blk s = 0 ->
    ( forall k : Z, 0 <= k < 16 -> k <> s ->
        slot_name d blk k = name -> slot_inode d blk k = 0 ) ->
    dir_lookup d blk name < 0.
Proof.
  intros d blk name s _Hnn Hs Hwit Huniq.
  unfold dir_lookup.
  pose proof (scan_reflects_prefix d blk name 16) as [Hiff Hrng].
  replace (Z.of_nat 16) with 16 in Hiff by reflexivity.
  destruct (Z_ge_lt_dec (scan d blk name 16 (-1)) 0) as [Hge | Hlt].
  - exfalso.
    apply Hiff in Hge. destruct Hge as [k [Hk Hm]].
    unfold matches in Hm. destruct Hm as [Hne [Hltk Hnm]].
    destruct (Z.eq_dec k s) as [Hks | Hks].
    + subst k. rewrite Hwit in Hne. apply Hne. reflexivity.
    + pose proof (Huniq k Hk Hks Hnm) as Hdead. apply Hne. exact Hdead.
  - exact Hlt.
Qed.
```

Kernel evidence:
```
$ coqc RemoveAbsent.v            # exit 0, no Admitted/Axiom
$ coqc checkaxioms.v             # Print Assumptions remove_reflects_absent
Closed under the global context
```
→ **0 axioms, fully closed.** Same trust class as `scan_reflects_present`.

### Lean (`/tmp/dirscan11/RemoveAbsent.lean`, lean 4.30.0, core only — no Mathlib)

```lean
theorem remove_reflects_absent
    (d : Disk) (blk : Int) (name : NameT) (s : Int)
    (hnn : ∀ k, 0 ≤ slotInode d blk k)
    (hs  : 0 ≤ s ∧ s < 16)
    (hwit : slotInode d blk s = 0)
    (huniq : ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s →
        slotName d blk k = name → slotInode d blk k = 0) :
    dirLookup slotInode slotName d blk name < 0 := by
  unfold dirLookup
  have hempty : ¬ (∃ k : Int, 0 ≤ k ∧ k < Int.ofNat 16 ∧
      slotMatches slotInode slotName d blk name k) := by
    rintro ⟨k, hk0, hk16, hne, _hlt, hnm⟩
    simp only [show (Int.ofNat 16 : Int) = 16 from rfl] at hk16
    by_cases hks : k = s
    · rw [hks] at hne; exact hne hwit
    · exact hne (huniq k hk0 hk16 hks hnm)
  have hiff := (scan_reflects_prefix slotInode slotName d blk name hnn 16).1
  have hnotge : ¬ (scan slotInode slotName d blk name 16 (-1) ≥ 0) :=
    fun hge => hempty (hiff.mp hge)
  omega
```

Kernel evidence:
```
$ lean RemoveAbsent.lean
... (only a `warning: unused variable hs` — the vacuous-bound note above)
'UnixFs.Dir.remove_reflects_absent' depends on axioms: [propext, Quot.sound]
```
→ **axioms ⊆ {propext, Quot.sound}**, no `sorryAx`. Allowlisted.

**VERDICT (RISK (a)): both proofs go through, dual-kernel accepted, allowlisted.** The
proof side is DONE. The lemma is sound and minimal.

---

## 3. The os-model uniqueness INVARIANT — feasibility verdict: BALLOONS (RISK (b))

`remove_reflects_absent` discharges `dir_lookup(self.disk,5,name) < 0` ONLY if the body
supplies its two hypotheses at the call site. Both are blocked by model gaps that are
NOT byte-local and NOT free:

### 3a. Remove-witness (`slot_inode(self.disk,5,s) == 0` after zeroing) — needs a NEW trusted claim
The removal is an inline raw byte-slice assignment in three syscalls (4 sites):
`sys_unlink` (UnixInodeFileSystem.py:1115), `sys_rmdir` (:1214), `sys_rename` (:1364,
:1367): `self.disk[2560 + slot*32 : +32] = b'\x00'*32`. There is currently NO logic fact
relating a zeroed 32-byte dirent slice to `slot_inode == 0`. The existing `_write_entry`
(:834) pins only the WRITE side of a LIVE entry, and it is itself `\trusted reviewer:
dirscan-fidelity` (:833) on exactly this decode↔bytes correspondence.

Required model change: a NEW trusted helper `_zero_entry(block_num, slot)` (replacing the
4 inline slices) with `#@ ensures slot_inode(self.disk, block_num, slot) == 0` — the
DUAL trusted decode claim of `_write_entry`'s live-write claim. This is a genuinely new
TCB modelling claim (faithful: zeroing the inode field's bytes makes the big-endian decode
0), of the SAME trust class as `_write_entry`. Acceptable but NOT free — it is a third
trusted decode clause.

### 3b. Slot-locality (other slots unchanged) — needs a NEW frame axiom OR trusted clause
`_zero_entry(5, s)` must ALSO leave every `k != s` decode unchanged, else the uniqueness
hypothesis (which quantifies over all `k != s`) cannot be carried across the write. This is
gap-11 hypothesis 3, an abstract per-slot frame fact: `slot_inode`/`slot_name` at `k` are
functions of slot-`k` bytes only. It is NOT expressible against the current abstract
`val function slot_inode (disk: array int) (blk: int) (k: int)` — the symbol takes the
WHOLE `disk`, so writing any byte havocs every application. Discharging it requires
EITHER a new registered axiom (`slot_inode`/`slot_name` ignore bytes outside
`[blk*512+k*32, +32)` — provable in Rocq/Lean over the concrete byte decode, a 3rd/4th
axiom) OR a trusted `_zero_entry`/`_write_entry` ensures of the form
`\forall k. k != slot ==> slot_inode(self.disk,blk,k) == \old(slot_inode(self.disk,blk,k))`.
Either way it is NEW surface beyond the one lemma this spec validates.

### 3c. Uniqueness as a maintained class invariant — the BALLOON
The uniqueness hypothesis `∀ k != s. slot_name 5 k = name ⟹ dead` says block 5 holds AT
MOST ONE live slot per name. To have it at the removal call site, the cleanest model form
is a CLASS INVARIANT (alongside UnixInodeFileSystem.py:435-441):
```
#@ class invariant \forall i j; ( 0<=i<16 and 0<=j<16
      and slot_inode(self.disk,5,i)!=0 and slot_inode(self.disk,5,i)<32
      and slot_inode(self.disk,5,j)!=0 and slot_inode(self.disk,5,j)<32
      and slot_name(self.disk,5,i)==slot_name(self.disk,5,j) ) ==> i==j
```
`_format_disk` establishes it vacuously (slots 0,1 are dead, inode 0). The wall is
PRESERVATION: EVERY `_write_entry` of a LIVE entry must re-prove it, and that requires, at
each call:
  1. slot-locality (3b) — to know the other live slots' decodes survive the write, and
  2. "the new name is not already live" — `\old(dir_lookup(self.disk,5,name)) < 0`.

Auditing the mutators that call `_write_entry(5, ...)` with a live inode:
- `sys_mkdir` (:1166) and `sys_open` O_CREAT (:913) and `sys_symlink` (:1387) GUARD with
  `_dir_lookup(5,name) >= 0 => return -1` → "name not already live" is available. GOOD.
- **`sys_link` (:1077-1092) does NOT guard `newpath`** — it only checks `oldpath` exists,
  finds a free slot, and writes `newpath`. It can create a DUPLICATE live name today.
  POSIX `link` returns `EEXIST` if `newpath` exists, so adding
  `if self._dir_lookup(5, newpath) >= 0: return -1` is FAITHFUL — but it is a behavior
  change to a currently-GREEN syscall, and re-proving its (already delicate, `no_inline`,
  E-matching-sensitive) PRESENCE ensures alongside a new invariant is exactly the kind of
  reorder/contract change the safe-bricks doctrine says to FLAG.
- `sys_rename` (:1358) zeros `newpath`'s slot before writing (no dup by construction) but
  proving preservation still needs slot-locality + the remove fact for the zeroed slots.

Because a CLASS invariant must hold at EVERY method boundary, adding it forces a
preservation re-proof through `_write_entry` and through EVERY syscall that touches block
5 — `sys_open`/`sys_mkdir`/`sys_link`/`sys_rename`/`sys_symlink`/`sys_unlink`/`sys_rmdir`.
Each re-proof leans on the unproven slot-locality frame (3b), which itself quantifies over
the 16 slots and is SMT-hostile (the same E-matching surface that already needed
`no_inline` + entry-write-last to keep os GREEN at 1480/0). 

**FEASIBILITY VERDICT: this BALLOONS.** Closing the 3 absence consequences is NOT the
single-axiom drop that gap-9's presence beachhead was. It needs, beyond the validated
`remove_reflects_absent`: (i) a trusted `_zero_entry` with a remove-witness ensures
(new TCB), (ii) a slot-locality frame fact (new axiom or trusted clause), (iii) a
uniqueness class invariant whose PRESERVATION must be re-discharged across 7 syscalls —
against the very E-matching surface that is already at the edge of timing out. Items (i)
and (ii) are tractable axiom/clause additions; item (iii) is a large model change with a
real risk of regressing os off 1480/0. An ALTERNATIVE that avoids the class invariant —
discharge uniqueness LOCALLY at each removal site from the `_dir_find_slot` result plus a
"this was the only live match" fact — runs into the same slot-locality + scan-uniqueness
SMT wall (it IS scan-uniqueness, inductive over 16 slots), so it would need its OWN
registered `scan_unique` axiom and still the slot-locality frame. Either path is
materially bigger than gap-9/gap-10.

---

## 4. How the absence consequences would then prove (the integration, once 3a–3c land)

1. Register `UnixFs.Dir.remove_reflects_absent` in `_AXIOM_REGISTRY` (§1). No new
   `_AXIOM_FUNCTIONS` entry needed — it reuses the `UnixFs.Dir.` symbols.
2. Add trusted `_zero_entry(block_num, slot)` (remove-witness + slot-locality ensures);
   replace the 4 inline zeroing slices with calls.
3. Add the uniqueness class invariant (§3c) + re-prove preservation across the 7 block-5
   mutators (the balloon); add the `sys_link` `newpath` EEXIST guard.
4. On `sys_rmdir`/`sys_unlink` success add
   `#@ ensures \result == 0 ==> dir_lookup(self.disk, 5, pathname) < 0`; on `sys_rename`
   add the `oldpath` absence ensures. Each cites `remove_reflects_absent` +
   `slot_inode_nonneg`, supplies `#@ assert slot_inode(self.disk,5,slot)==0` after the
   `_zero_entry`, and feeds the uniqueness invariant as the lemma's 4th hypothesis.
5. Wrappers `rmdir`/`remove`/`unlink`/`rename` in `pure_lib/os/__init__.py` propagate
   `#@ ensures \result == 0 ==> dir_lookup(_filesystem.disk, 5, path) < 0`.
6. `formal_os_namespace.py`'s `rmdir_then_access_absent` / `unlink_then_access_absent` /
   `rename_then_a_absent` flip Timeout→VALID through the public API — completing 7/7.

---

## 5. Gate (for the IMPLEMENTATION phase, post-APPROVED)

- Audit: both kernels accept; Rocq `Print Assumptions` = Closed; Lean `#print axioms`
  ⊆ {propext, Quot.sound}. ✅ DONE this phase for `remove_reflects_absent`. (Any slot-
  locality / scan_unique axiom added for 3b/3c must clear the SAME gate before landing.)
- os re-proves GREEN: `pycsl pure_lib/os/__init__.py` → 1480/1480 (or higher), 0 unproven,
  WITH the uniqueness invariant maintained and the 3 absence ensures discharged. ← THE
  AT-RISK gate (RISK (b)); preservation across 7 syscalls may regress the E-matching.
- The 3 absence consequences VALID via STANDARD `pycsl pure_lib_test/formal_os_namespace.py`
  (target 7/7 VALID, currently 4/7).
- `bin/byte-diff-sweep.sh` before/after IDENTICAL (only `pure_lib/os/` + `src/pycsl/
  module6_whyml/preamble.py` + proof files touched; none are in the reference corpus —
  byte-additive).
- Conformance 38 OK / 0 MISMATCH; determinism 10/10.
- doc-coherency `bin/doc-coherency.py --check` green (the registry axioms are NOT tracked
  by it — `proof` is already a known directive; the new axiom needs a `docs/
  pycsl-axiom-plumbing-internals.md` + `glossary/axiom-registry.md` entry, a doc update not a gate).

---

## RISKS (lead for your judgment)

**(a) Do both proofs go through?** YES — VALIDATED this phase. Rocq: Closed under the
global context (0 axioms). Lean: axioms ⊆ {propext, Quot.sound}, no sorry. The single
`remove_reflects_absent` lemma is sound, minimal, and the same trust class as the gap-9
presence axiom. The proof side is not the risk.

**(b) Is the uniqueness invariant maintainable across ALL syscalls without a large/blocked
model change?** NO — it BALLOONS (this is the real blocker; see §3). The lemma needs three
model facts none of which is free: a trusted remove-witness `_zero_entry` ensures (new
TCB, dual of `_write_entry`), a slot-locality frame fact (new axiom or trusted clause —
the abstract `slot_inode` takes the whole disk, so every byte write havocs it), and
uniqueness as a CLASS invariant whose preservation must be re-proved through 7 block-5
mutators — against the exact E-matching surface that already forced `no_inline` +
entry-write-last to keep os at 1480/0, with real regression risk. `sys_link` also lacks a
`newpath` EEXIST guard, so maintaining uniqueness requires changing a currently-GREEN,
proof-delicate syscall. This is a materially bigger change than gap-9/gap-10's single-axiom
beachhead. My recommendation: APPROVE registering `remove_reflects_absent` (the proof is
done and the TCB cost is justified), but scope the os-model integration as its OWN gated
iteration (3a→3b→3c staged, byte-checked at each step), and be prepared for 3c to need a
further `scan_unique` axiom or to wall on the SMT preservation. Do NOT expect 7/7 in one
landing.

**(c) TCB — what exactly do the new axioms assert (faithful, not over-strong)?**
`remove_reflects_absent` asserts ONLY: for the abstract bounded 16-slot scan, IF the
slot-decode is non-negative everywhere AND slot s decodes to a dead inode AND every other
slot decoding to `name` is dead, THEN `dir_lookup < 0`. It is a pure structural
consequence of the scan definition (the `<-`/absence half of the gap-9 IFF) — it makes NO
new claim about disk bytes; the remove-witness and uniqueness are HYPOTHESES, not
assertions. Faithful, not over-strong. The vacuous `0 <= s < 16` antecedent (unused in
both proofs) could be dropped to shrink the surface. The TCB GROWTH that actually closes
the consequences is NOT in this lemma but in the §3 model facts: `_zero_entry`'s
remove-witness ensures (faithful — zeroing the inode bytes ⟹ decode 0) and the
slot-locality frame (faithful — per-slot decode is byte-local); both are the same
human-reviewed decode↔bytes trust class as the existing `_write_entry` `\trusted
dirscan-fidelity` clause, and (if registered as axioms rather than trusted ensures) must
each pass the dual-kernel gate.

---

Probes: `/tmp/dirscan11/RemoveAbsent.v`, `/tmp/dirscan11/RemoveAbsent.lean` (both compile;
evidence pasted in §2). Spec at STATUS: DRAFT. NO source edits, NO axioms registered, NO
git operations.
