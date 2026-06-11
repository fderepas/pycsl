STATUS: IMPLEMENTED-PARTIAL — axiom landed + os GREEN (1807/0) + binding REAL (non-vacuous); end-to-end API flip BLOCKED on a pre-existing module-global/logic-program-duality gap (NOT DONE — honest, per the approval's "the API flip is the proof the binding is real")

<!-- IMPLEMENTATION REPORT (gap-9, this dispatch) — NOT git-committed.
LANDED & GREEN:
- Registry: src/pycsl/module6_whyml/preamble.py — `UnixFs.Dir.scan_reflects_present` (the IFF, WITH the explicit
  `forall j. 0<=j<16 -> slot_inode disk blk j >= 0` antecedent mirroring the proofs' `slot_inode_nonneg`/`hnn`
  hypothesis) + companion `UnixFs.Dir.slot_inode_nonneg` (discharges that antecedent); `_AXIOM_FUNCTIONS["UnixFs.Dir."]`
  declares `slot_inode`/`slot_name`/`dir_lookup` as `val function`.
- Proofs: unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/UnixDirScan.{v,lean} (both theorems). audit_proof
  --reverify CLEAN: Rocq "Closed under the global context" (0 axioms) for BOTH; Lean axioms ⊆ {propext, Quot.sound}.
- RISK-2 BINDING IS REAL (NON-VACUOUS): `_dir_lookup` ensures `\result == dir_lookup(self.disk, block_num, pathname)`;
  `_write_entry` (trusted-clause) ensures the written live slot makes `slot_inode/slot_name(self.disk, blk, slot)` return
  `(inode_num, name)` — the existential witness. `sys_access`/`sys_mkdir` then PROVE the `dir_lookup(self.disk,5,name)>=0`
  presence postcondition FROM those bound symbols + the cited axiom. These were gap-9 Timeouts (14.6M/11.6M/18.8M steps);
  they are now Valid via the citation — concrete proof the axiom constrains the REAL scan. os re-proves 1807/0 GREEN.
- Byte-additive: bin/byte-diff-sweep.sh — 0 corpus drivers change (the axiom fires only where cited). os itself changes
  (it cites the axiom — expected). Conformance 38/38. doc-coherency green (no new `#@` directive); UnixFs.Dir.* family
  added to docs/glossary/axiom-registry.md.
- TOOL ENABLERS (gated, byte-identical for all existing files): axiom `val function` symbols bind raw in contracts
  (`_axiom_logic_funcs`); a 4th method-contract-propagation map (`field+param+result`, A2c+) so an ensures mixing a
  self-field AND a param (`(\result==0)<==>dir_lookup(self.disk,5,pathname)>=0`) crosses a module-global method call.

REMAINING WALL (why NOT DONE): formal_os_namespace.py's mkdir->access-present does NOT yet flip Valid through the public
API. The wrappers' presence view `dir_lookup(_filesystem.disk, 5, name) >= 0` references the module GLOBAL `_filesystem`.
A module global is emitted as a program `let` (and reaches a pure-API driver as an opaque program `get_disk`), which is
ILLEGAL in the logic `ensures`/predicate the presence view needs. Bridging it requires either a logic/program global
duality OR crossing the `_filesystem` global+record into the driver (which cascades into method-inlining of the other
imported wrappers). Both are pre-existing import-architecture gaps independent of the gap-9 axiom (the gap-7 §B /
"Method-call contract gap" family). The os-LEVEL non-vacuity IS demonstrated (the syscall postconditions prove only via
the binding); the END-TO-END API flip needs that separate gap closed. Honesty over green: reported, not faked.
-->

<!-- COORDINATION APPROVAL (editorial) — TCB addition JUDGED and approved:
- THE AXIOM IS APPROVED. Both kernels accept the FULL proof (Rocq "Closed under the global context" — zero
  axioms; Lean [propext, Quot.sound] — core allowlist, no Mathlib). It is faithful, not over-strong: the
  proof is by induction on the slot index and PARAMETRIC over the per-slot decode (slot_inode/slot_name
  abstract), so it cannot smuggle in codec assumptions — it is the scan loop's actual closed form. The
  single side condition (slot_inode >= 0, unsigned-byte) is an EXPLICIT antecedent, discharged in WhyML by
  the os byte-range invariant. Trust class = the existing bitmap/struct fs axioms (cross-check verifies
  symbol-name agreement; the WhyML↔Python _dir_lookup fidelity is human-reviewed, as for those).
- MANDATORY (risk 2 — the load-bearing detail): the implementation MUST bind `_dir_lookup`'s contract to
  the registered `dir_lookup` symbol AND supply `slot_inode >= 0` from the byte-range invariant, so the
  cited ensures constrain the REAL scan and do not prove a vacuous postcondition. THE PROOF THAT THE
  BINDING IS REAL: `formal_os_namespace.py`'s mkdir→present must flip Unknown→VALID THROUGH THE PUBLIC API
  (not just os re-proving) — that is the end-to-end evidence the axiom actually closes the consequence.
- SCOPE: beachhead = mkdir + access this iteration. rmdir/unlink/link/rename are a follow-on turn.
Acceptance bar: audit_proof clean (both kernels accept, no extraneous axioms); os re-proves GREEN with the
3 Timeout goals now Valid; formal_os_namespace mkdir→present flips Unknown→VALID through the API;
full-corpus byte-diff ADDITIVE (the axiom fires only where cited — bin/byte-diff-sweep.sh); conformance
38/38; doc green. On success set STATUS: DONE. -->

# Convergence spec — iteration 9 (`UnixFs.Dir.scan_reflects_present`: the inductive directory-scan reflection axiom — TCB addition)

**Loop:** `config/skills/pycsl-stdlib-coverage` — Step 5b (axiom registry).
**Input:** `11-0743-convergence-gap-9.md` (the `name_present` beachhead WALL; the precise lemma in its §Lemma).
**Iteration:** N = 9.
**Phase:** SPEC ONLY. No `src/pycsl/` edit, no `_AXIOM_REGISTRY` edit, no model re-application. Implementation follows after coordination sets STATUS: APPROVED (adding an axiom is a TCB decision).

This spec answers the make-or-break question: **does the inductive scan-reflects-present lemma actually prove in Rocq AND Lean?** Answer: **YES — both kernels accept, with no non-allowlisted assumptions.** Evidence is pasted below.

---

## 1. Lemma recap

`_dir_lookup(blk, name)` (`pure_lib/os/UnixInodeFileSystem.py:713`) is a linear scan over the 16 directory slots of block `blk`. The lemma is its closed form:

> The bounded scan returns a non-negative inode IFF some live slot `k < 16` decodes to `name`.

i.e. `dir_lookup disk blk name >= 0  <->  (∃ k. 0 <= k < 16 ∧ slot is live ∧ slot decodes to name)`. At fixed root block 5 this is exactly the os model's `name_present(name)`, so `access(name) == 1 <-> name_present(name)` and `mkdir(name) == 0 -> name_present(name)` discharge through the public API.

SMT (Alt-Ergo/Z3) times out (gap-9: 14.6M / 11.6M / 18.8M steps) because closing the IFF requires synthesizing the loop induction connecting the running `found` to the existential. Per the family rule (an SMT wall on an inductive loop property → a cross-validated Rocq + Lean axiom), this is sourced from the proof assistants and imported as a Why3 preamble axiom.

---

## 2. Tooling availability

| Tool | Path | Version | Status |
|------|------|---------|--------|
| Rocq (`coqc`) | `~/.opam/coq-4.14/bin/coqc` | The Coq Proof Assistant 8.20.1 (OCaml 4.14.2) | RUNNABLE |
| Lean (`lean`) | `~/.elan/bin/lean` | Lean 4.30.0 | RUNNABLE |
| Why3 | `~/.opam/coq-4.14/bin/why3` | 1.8.2 | RUNNABLE (used to typecheck the proposed axiom block) |

`rocq` (the new binary name) is NOT on PATH; `coqc` is, and is what the project already uses (`bin/check-proof-crosscheck.sh`, `audit_proof_reverify`). No tooling blocker.

---

## 3. THE VALIDATED PROOFS (the key deliverable)

Both proofs were written in `/tmp/dirscan/` and run through the actual kernels. Both ACCEPT.

### 3.1 Modelling decision (faithfulness — read before the proofs)

The scan is modelled as a `Fixpoint`/recursive `def` over the **prefix length** `i` (slot index `0..16`), parameterised by **abstract** per-slot decode functions `slot_inode`, `slot_name` and an abstract block/disk type. This is deliberate and is what makes the axiom faithful:

* The proof is **parametric** over `slot_inode`/`slot_name` — it proves the reflection property for ANY per-slot decode, so it does NOT bake in (and cannot accidentally over-assume) anything about the byte-codec. The codec round-trip is a *separate* already-proven fact (`UnixInodeFileSystem.py:258–292`); this lemma is purely about the *accumulation over the slot loop*, which is exactly the inductive part SMT cannot do.
* The scan body mirrors `_dir_lookup` exactly: it recurses on the prefix `j` first, then tests slot `j` with the guard `inode != 0 ∧ inode < 32 ∧ name == pathname`, keeping the LAST match. The IFF is insensitive to first-vs-last match.
* **One semantic side-condition** beyond the scan structure: `slot_inode d blk k >= 0` (a decoded inode is non-negative — it is read from unsigned disk bytes). This is the model's unsigned-byte inode field and is made an explicit hypothesis (`slot_inode_nonneg` / `hnn`) rather than smuggled in. It surfaces as an explicit antecedent of the closed theorem (see §3.4), and in WhyML it is discharged by the os model's own byte-range invariant. This is the ONLY assumption the trust judgment must weigh beyond "the scan is a 16-slot loop".

### 3.2 Rocq proof — ACCEPTS, closed under the global context (no axioms)

Verified with `coqc UnixDirScan.v` (exit 0) and `Print Assumptions`:

```
$ coqc UnixDirScan.v ; echo EXIT=$?
EXIT=0

$ coqc -R . "" check.v          (* Require Import UnixDirScan. Print Assumptions UnixFs.Dir.scan_reflects_present. *)
Closed under the global context
EXIT=0
```

`Closed under the global context` is the STRONGEST Rocq result — the theorem uses ZERO axioms (`ROCQ_NO_AXIOMS_MARKER` in `proof_axiom_allowlist.py`). The full proof (`UnixFs.Dir` namespace, theorem `scan_reflects_present`, no `Admitted`/`Axiom`):

```coq
Require Import Coq.ZArith.ZArith.
Require Import Coq.Bool.Bool.
Require Import Lia.
Open Scope Z_scope.

Module UnixFs.
Module Dir.
Section Scan.

Variable disk : Type.
Variable name_t : Type.
Variable slot_inode : disk -> Z -> Z -> Z.
Variable slot_name  : disk -> Z -> Z -> name_t.
Variable eqn : name_t -> name_t -> bool.
Hypothesis eqn_spec : forall a b, eqn a b = true <-> a = b.
(* faithful model fact: decoded inode read from unsigned bytes is non-negative *)
Hypothesis slot_inode_nonneg : forall d blk k, 0 <= slot_inode d blk k.

Definition matches (d : disk) (blk : Z) (name : name_t) (k : Z) : Prop :=
  slot_inode d blk k <> 0 /\ slot_inode d blk k < 32 /\ slot_name d blk k = name.

Fixpoint scan (d : disk) (blk : Z) (name : name_t) (i : nat) (found : Z) : Z :=
  match i with
  | O => found
  | S j =>
      let f := scan d blk name j found in
      let zj := Z.of_nat j in
      if andb (negb (Z.eqb (slot_inode d blk zj) 0))
              (andb (Z.ltb (slot_inode d blk zj) 32)
                    (eqn (slot_name d blk zj) name))
      then slot_inode d blk zj
      else f
  end.

Lemma scan_reflects_prefix : forall (d : disk) (blk : Z) (name : name_t) (i : nat),
  ( (scan d blk name i (-1) >= 0)
    <-> (exists k : Z, 0 <= k < Z.of_nat i /\ matches d blk name k) )
  /\ ( scan d blk name i (-1) >= 0 -> scan d blk name i (-1) < 32 ).
Proof.
  intros d blk name i. induction i as [| j IH].
  - simpl. split.
    + split.
      * intro H. lia.
      * intros [k [Hk _]]. lia.
    + intro H. lia.
  - destruct IH as [IHiff IHrng].
    simpl.
    set (zj := Z.of_nat j) in *.
    remember (andb (negb (Z.eqb (slot_inode d blk zj) 0))
                   (andb (Z.ltb (slot_inode d blk zj) 32)
                         (eqn (slot_name d blk zj) name))) as guard eqn:Hguard.
    destruct guard.
    + symmetry in Hguard.
      apply andb_true_iff in Hguard. destruct Hguard as [Hne Hrest].
      apply andb_true_iff in Hrest. destruct Hrest as [Hlt Heqn].
      apply negb_true_iff in Hne. apply Z.eqb_neq in Hne.
      apply Z.ltb_lt in Hlt.
      apply eqn_spec in Heqn.
      assert (Hm : matches d blk name zj).
      { unfold matches. repeat split; assumption. }
      split.
      * split.
        -- intro _H. exists zj. split; [ split; [ apply Nat2Z.is_nonneg | lia ] | exact Hm ].
        -- intro _H. pose proof (slot_inode_nonneg d blk zj). lia.
      * intro _H. lia.
    + symmetry in Hguard.
      split.
      * rewrite IHiff. split.
        -- intros [k [Hk Hm]]. exists k. split; [ split; [ lia | lia ] | exact Hm ].
        -- intros [k [Hk Hm]].
           assert (Hkj : k < zj \/ k = zj) by lia.
           destruct Hkj as [Hklt | Hkeq].
           ++ exists k. split; [ split; [ lia | lia ] | exact Hm ].
           ++ subst k. exfalso.
              unfold matches in Hm. destruct Hm as [Hne [Hlt Heq]].
              assert (Hg : andb (negb (Z.eqb (slot_inode d blk zj) 0))
                                (andb (Z.ltb (slot_inode d blk zj) 32)
                                      (eqn (slot_name d blk zj) name)) = true).
              { apply andb_true_iff. split.
                - apply negb_true_iff. apply Z.eqb_neq. exact Hne.
                - apply andb_true_iff. split.
                  + apply Z.ltb_lt. exact Hlt.
                  + apply eqn_spec. exact Heq. }
              rewrite Hg in Hguard. discriminate.
      * exact IHrng.
Qed.

Definition dir_lookup (d : disk) (blk : Z) (name : name_t) : Z :=
  scan d blk name 16 (-1).

Theorem scan_reflects_present : forall (d : disk) (blk : Z) (name : name_t),
  (dir_lookup d blk name >= 0)
  <-> (exists k : Z, 0 <= k < 16 /\ matches d blk name k).
Proof.
  intros d blk name. unfold dir_lookup.
  pose proof (scan_reflects_prefix d blk name 16) as [Hiff _].
  replace (Z.of_nat 16) with 16 in Hiff by reflexivity.
  exact Hiff.
Qed.

End Scan.
End Dir.
End UnixFs.
```

### 3.3 Lean 4 proof — ACCEPTS, axioms ⊆ allowlist

Verified with `lean UnixDirScan.lean` (exit 0) and `#print axioms`:

```
$ lean UnixDirScan.lean ; echo EXIT=$?
EXIT=0

$ #print axioms UnixFs.Dir.scan_reflects_present
'UnixFs.Dir.scan_reflects_present' depends on axioms: [propext, Quot.sound]
```

`propext` and `Quot.sound` are BOTH in `LEAN_KERNEL_AXIOM_ALLOWLIST` (`proof_axiom_allowlist.py:36`: `propext`, `Classical.choice`, `Quot.sound`). No non-allowlisted assumption. Core Lean only — no Mathlib. The full proof (`UnixFs.Dir` namespace, theorem `scan_reflects_present`, no `sorry`):

```lean
namespace UnixFs.Dir

variable {Disk : Type} {NameT : Type}
variable (slotInode : Disk → Int → Int → Int)
variable (slotName  : Disk → Int → Int → NameT)
variable [DecidableEq NameT]

def slotMatches (d : Disk) (blk : Int) (name : NameT) (k : Int) : Prop :=
  slotInode d blk k ≠ 0 ∧ slotInode d blk k < 32 ∧ slotName d blk k = name

def scan (d : Disk) (blk : Int) (name : NameT) : Nat → Int → Int
  | 0,     found => found
  | (j+1), found =>
      let f := scan d blk name j found
      let zj : Int := Int.ofNat j
      if slotInode d blk zj ≠ 0 ∧ slotInode d blk zj < 32 ∧ slotName d blk zj = name
      then slotInode d blk zj
      else f

theorem scan_reflects_prefix
    (d : Disk) (blk : Int) (name : NameT)
    (hnn : ∀ k, 0 ≤ slotInode d blk k) :
    ∀ i : Nat,
      ((scan slotInode slotName d blk name i (-1) ≥ 0)
        ↔ (∃ k : Int, 0 ≤ k ∧ k < Int.ofNat i ∧
              slotMatches slotInode slotName d blk name k))
      ∧ (scan slotInode slotName d blk name i (-1) ≥ 0 →
           scan slotInode slotName d blk name i (-1) < 32) := by
  intro i
  induction i with
  | zero =>
    simp only [scan]
    constructor
    · constructor
      · intro h; exact absurd h (by decide)
      · rintro ⟨k, hk0, hki, _⟩; simp at hki; omega
    · intro h; exact absurd h (by decide)
  | succ j ih =>
    obtain ⟨ihiff, ihrng⟩ := ih
    simp only [scan]
    have hofj : (0 : Int) ≤ Int.ofNat j := Int.natCast_nonneg j
    have hsucc : (Int.ofNat (j+1) : Int) = Int.ofNat j + 1 := by exact_mod_cast rfl
    by_cases hguard :
        slotInode d blk (Int.ofNat j) ≠ 0 ∧ slotInode d blk (Int.ofNat j) < 32 ∧
          slotName d blk (Int.ofNat j) = name
    · rw [if_pos hguard]
      obtain ⟨hne, hlt, heq⟩ := hguard
      have hm : slotMatches slotInode slotName d blk name (Int.ofNat j) := ⟨hne, hlt, heq⟩
      have hinn : 0 ≤ slotInode d blk (Int.ofNat j) := hnn (Int.ofNat j)
      refine ⟨⟨fun _ => ⟨Int.ofNat j, by omega, by omega, hm⟩, fun _ => by omega⟩,
              fun _ => by omega⟩
    · rw [if_neg hguard]
      refine ⟨?_, ihrng⟩
      rw [ihiff]
      constructor
      · rintro ⟨k, hk0, hkj, hm⟩
        exact ⟨k, hk0, by omega, hm⟩
      · rintro ⟨k, hk0, hkj1, hm⟩
        rcases (show k < Int.ofNat j ∨ k = Int.ofNat j by omega) with hklt | hkeq
        · exact ⟨k, hk0, hklt, hm⟩
        · exfalso; rw [hkeq] at hm; exact hguard hm

def dirLookup (d : Disk) (blk : Int) (name : NameT) : Int :=
  scan slotInode slotName d blk name 16 (-1)

theorem scan_reflects_present
    (d : Disk) (blk : Int) (name : NameT)
    (hnn : ∀ k, 0 ≤ slotInode d blk k) :
    (dirLookup slotInode slotName d blk name ≥ 0)
      ↔ (∃ k : Int, 0 ≤ k ∧ k < 16 ∧ slotMatches slotInode slotName d blk name k) := by
  have h := (scan_reflects_prefix slotInode slotName d blk name hnn 16).1
  simpa [dirLookup] using h

end UnixFs.Dir
```

(Note: `matches` is a reserved Lean keyword, so the Lean predicate is named `slotMatches`; the Rocq one is `matches`. This does NOT affect the cited theorem qualname `UnixFs.Dir.scan_reflects_present`, which `audit_proof` matches by namespace + theorem name in BOTH files.)

### 3.4 The closed (section-discharged) Rocq theorem type

After the `Section` closes, `slot_inode`/`slot_name`/`eqn`/`disk`/`name_t` become universally-quantified parameters and the two hypotheses become explicit antecedents — exactly mirroring the WhyML `forall` + abstract `val function` symbols:

```
UnixFs.Dir.scan_reflects_present
  : forall (disk name_t : Type)
      (slot_inode : disk -> Z -> Z -> Z) (slot_name : disk -> Z -> Z -> name_t)
      (eqn : name_t -> name_t -> bool),
    (forall a b, eqn a b = true <-> a = b) ->
    (forall d blk k, 0 <= slot_inode d blk k) ->
    forall d blk name,
      dir_lookup ... d blk name >= 0
      <-> (exists k, (0 <= k < 16) /\ matches ... d blk name k)
```

### 3.5 The audit_proof namespace-presence check passes for both

`audit_proof._parse_rocq_file` / `_parse_lean_file` on the two files both return `UnixFs.Dir.scan_reflects_present` (and `scan`, `dir_lookup`/`dirLookup`, etc.). Verified empirically — `q in qualnames` is `True` for both provers.

---

## 4. The registry + os-citation integration plan

### 4.1 `_AXIOM_REGISTRY` entry (`src/pycsl/module6_whyml/preamble.py`)

```python
# UnixFs.Dir — directory-scan reflection. The bounded scan over the 16
# root-directory slots returns a non-negative inode IFF some live slot
# decodes to `name`. INDUCTIVE over the slot loop (SMT times out:
# gap-9, 14.6M/11.6M/18.8M steps). Cross-validated by
# unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/UnixDirScan.{v,lean}
# (UnixFs.Dir.scan_reflects_present): induction on the prefix length +
# per-slot case split. Rocq: Closed under the global context (0 axioms);
# Lean: axioms ⊆ {propext, Quot.sound}. The slot_inode>=0 side condition
# (decoded inode from unsigned bytes) is discharged in WhyML by the os
# model's byte-range invariant.
"UnixFs.Dir.scan_reflects_present":
    "forall disk : array int. forall blk : int. forall name : string. "
    "( dir_lookup disk blk name >= 0 ) "
    "<-> "
    "( exists k : int. 0 <= k < 16 "
    "/\\ slot_inode disk blk k <> 0 "
    "/\\ slot_inode disk blk k < 32 "
    "/\\ slot_name disk blk k = name )",
```

### 4.2 `_AXIOM_FUNCTIONS` prefix entry

```python
"UnixFs.Dir.": [
    "val function slot_inode (disk: array int) (blk: int) (k: int) : int",
    "val function slot_name  (disk: array int) (blk: int) (k: int) : string",
    "val function dir_lookup (disk: array int) (blk: int) (name: string) : int",
],
```

**Validation evidence (why3 1.8.2):** the exact axiom block above (the three `val function` decls + the axiom body, with `use int.Int`, `use array.Array`, `use string.String`) typechecks, and a downstream goal `dir_lookup disk 5 name >= 0 <-> name_present(...)` is discharged by Alt-Ergo in **50 steps** from the axiom (the consequence the os contracts will cite). This confirms the emitted block is well-typed and the citation closes in ~0 SMT effort.

### 4.3 os-citation plan (model side — re-applies gap-9's reverted edits)

1. `pure_lib/os/UnixInodeFileSystem.py`, on `sys_access` and `sys_mkdir` (companions of the `_dir_lookup(5, …)` calls), cite:
   ```python
   #@ proof rocq UnixFs.Dir.scan_reflects_present
   #@ proof lean UnixFs.Dir.scan_reflects_present
   ```
   so the syscall postconditions relating the return code to `name_present` discharge in 0 steps.
2. `pure_lib/os/__init__.py`: re-add the `#@ inductive name_present` predicate and the `mkdir`/`access` wrapper `ensures` (`\result == 0 ==> name_present(filepath)`, `(\result == 1) <==> name_present(filepath)`); these propagate from the now-cited syscalls.
3. Proof files: add the two theorems to the EXISTING fs proof tree
   `unix-filesystem/UnixInodeFileSystem.proofs/rocq/` and `.../lean/`
   (alongside the bitmap/struct proofs). Either as new files (`UnixDirScan.v` / `UnixDirScan.lean`) or appended to `UnixInodeFileSystem.{v,lean}` — the cross-check (`bin/check-proof-crosscheck.sh`) and `audit_proof` index the whole dir. The cross-check is already wired to `unix-filesystem/UnixInodeFileSystem.py`; the `pure_lib/os` citations resolve to the same proof tree via the cross-check manifest.

---

## 5. The gate (implementation must pass ALL before APPROVED→landed)

1. **audit_proof clean (incl. `--reverify`):** namespace-presence passes for both provers (confirmed in §3.5); reverify recompiles and confirms Rocq `Closed under the global context` and Lean axioms ⊆ allowlist (confirmed in §3.2/§3.3). No non-allowlisted assumption.
2. **os re-proves with the citation:** `pure_lib/os/UnixInodeFileSystem.py` + `pure_lib/os/__init__.py` re-prove at **1804+/0 green**, the three previously-Timeout access/mkdir postconditions now Valid via the 0-step citation.
3. **formal test flips:** `pure_lib_test/formal_os_namespace.py` `mkdir_then_access_present` / `file_present_after_mkdir` flip **Unknown → Valid through the public API** (the convergence fixed point).
4. **byte-additive:** files NOT citing `UnixFs.Dir.*` emit byte-identically (the axiom block is gated on a cited qualname — `_emit` returns early when no `#@ proof` is present). Verify via `bin/byte-diff-sweep.sh`.
5. **conformance:** the reference corpus + conformance `*.expected.mlw` unchanged; full reference suite green.
6. **doc-coherency:** no new `#@` directive is added (citation reuses existing `#@ proof`), so `bin/doc-coherency.py --check` is unaffected; the axiom-registry addition is documented in `docs/cross-validated-spec-sources.md` per the GCD/Bitmap precedent.

---

## 6. RISKS — led by the TCB statement (for the coordination agent's trust judgment)

### 6.1 TCB statement — what this axiom asserts (the thing to trust)

Registering `UnixFs.Dir.scan_reflects_present` adds to the WhyML trust base the proposition:

> For any disk, block `blk`, and name, the logic symbol `dir_lookup disk blk name` is `>= 0` **iff** there exists a slot `k ∈ [0,16)` with `slot_inode disk blk k ∉ {0} ∪ [32,∞)` and `slot_name disk blk k = name`.

It is a faithful — not over-strong — statement of the scan, for three reasons:
* **It is exactly `_dir_lookup`'s closed form.** The proof's `scan` Fixpoint replicates the Python loop body and bound (16 slots, guard `inode != 0 ∧ inode < 32 ∧ name == pathname`, last-match retention). The axiom is `scan ... 16 (-1) >= 0 <-> ∃k<16. matches`, which is `scan_reflects_prefix` at `i=16` — the loop's actual postcondition, not a stronger claim.
* **It is parametric over the byte-codec.** The axiom quantifies over abstract `slot_inode`/`slot_name`; it asserts NOTHING about how bytes decode (that round-trip is proven separately and is not part of this TCB entry). So the axiom cannot smuggle in a codec assumption.
* **Its one side condition is explicit and modelled.** `slot_inode >= 0` is the unsigned-byte inode fact; it is an explicit antecedent in both kernels (§3.4) and is discharged in WhyML by the os byte-range invariant, not assumed away.

### 6.2 RISKS

* **[TCB] This is a genuine trust-base addition.** Like `UnixFs.Bitmap.bit_and_one_in_zero_one` and `UnixFs.Struct.*`, the WhyML axiom is assumed by Why3; its truth rests on the Rocq + Lean proofs (which DO close — §3) and on the **fidelity of the WhyML symbols to the os model**. The fidelity is checked by the proof-statement cross-check (symbol names agree across registry/Rocq/Lean) but is NOT machine-checked against the *Python* `_dir_lookup` body — that correspondence is a human-reviewed modelling claim, same trust class as the existing fs axioms.
* **[MODELLING — needs review at impl time] `dir_lookup`/`slot_inode`/`slot_name` are abstract `val function`s in WhyML.** The os model must actually emit/bind these symbols so that `_dir_lookup`'s body is connected to `dir_lookup` (and `name_present` to the existential). gap-9 only got the predicate to *emit*; the impl step must verify the wrapper VC genuinely uses the axiom (the §4.2 why3 spike confirms the axiom + a citing goal typecheck and prove, but the live os wiring — that `_dir_lookup`'s contract names `dir_lookup` and the byte-range invariant supplies `slot_inode >= 0` — is the load-bearing impl detail). If that binding is loose, the citation could prove a postcondition that doesn't actually constrain the real scan — the failure mode the cross-check guards but cannot fully close.
* **[SCOPE] Beachhead only.** This closes `mkdir`+`access` ⇒ `name_present`. The dual absence/presence ensures for `rmdir`/`unlink`/`link`/`rename` are OUT OF SCOPE (gap-9 §200) and will need their own (likely reusing the same axiom, plus a "removes the witness slot" companion).
* **[LOW] Lean uses `propext` + `Quot.sound`.** Both allowlisted (class 0b). Rocq uses zero axioms. No new kernel-axiom dependency is introduced beyond the already-accepted set.
* **[LOW] `string` is built-in in WhyML.** The §4.2 block uses `use string.String`; the live emission must match however Module6 currently brings strings into scope for the os module (the no-more-int faithful string view). Minor wiring, surfaced here so impl doesn't double-declare.

---

## Appendix — validation artifacts (throwaway, /tmp)

* `/tmp/dirscan/UnixDirScan.v` — Rocq proof (coqc 8.20.1, exit 0; `Print Assumptions` = Closed under the global context).
* `/tmp/dirscan/UnixDirScan.lean` — Lean proof (lean 4.30.0, exit 0; `#print axioms` = [propext, Quot.sound]).
* `/tmp/dirscan/dir_axiom.mlw` — WhyML axiom-block typecheck + 50-step Alt-Ergo discharge of the cited consequence (why3 1.8.2).

These are throwaway validation files. The impl phase ships the proofs into `unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/` (§4.3).
