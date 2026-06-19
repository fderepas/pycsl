# `_zero_entry` de-trust 6→5 — ROBUST in the FULL body gate (RETIRES)

**Date:** 2026-06-19 17:45
**Worktree:** `.claude/worktrees/agent-a5d64cceca49a73d7` (nothing committed; STOP-AT-PROPOSAL)
**Patch:** `getting-better/PROPOSAL-zero-entry-detrust-v2-robust.patch` (the COMPLETE de-trust:
v1 base + the v2 robustness fix; apply with `git apply` to clean HEAD)

## BOTTOM LINE

`_zero_entry` NOW retires `\trusted` 6→5 robustly. In the FULL body gate (`pycsl
pure_lib/os/UnixInodeFileSystem.py`), run **×2**, `_zero_entry` has **0 non-Valid** — every
Assertion AND Postcondition Valid, with **byte-identical step counts across both runs**
(deterministic, no run-to-run flip). The only residual in the full gate is the pre-existing
`sys_rename` GAP (×2 Timeout — the documented baseline). No relocated explosion across any of
the 7 dir helpers. All four genuineness probes clean. `__init__` gate SUCCESS / 0 non-Valid.
Corpus byte-diff = 0 changes. New corollary cross-validated zero-TCB Rocq + Lean.

## THE BUG (prior v1 route)

The v1 de-trust folded the marker DIRECTLY from `_blit_dir_entry`'s ensures in a single
`#@ assert dir_blit_marker(...)`. That marker-ESTABLISHMENT goal was monolithic: it embedded
the quantifier-to-quantifier **byte-region frame bridge** (from the helper's `∀b` frame ensures
to the marker's `∀b` region-frame conjunct) INSIDE the establishment step. In `--fun` isolation
it proved Valid (~314K steps), but the full-module aggregate E-matching context tipped that one
monolithic step over the prover step budget → **Unknown in the FULL gate** → the de-trust red the
gate with 1 unproven Assertion (a regression, not a retirement).

## THE FIX (Option 1 corollary + Option 2-style assert restructuring)

Two complementary, doctrine-clean moves — NO bare `\trusted`, NO weakening, NO widened trigger:

1. **New zero-intro corollary `dir_blit_marker_intro_zero`** (cross-validated, zero-TCB). The
   general `dir_blit_marker_intro` carries EIGHT antecedents; for a ZEROED entry the name is
   EMPTY (`String.length name = 0`), so the two per-char `∀i` antecedents are VACUOUS, the
   len-bounds are trivial, and the null-pad collapses to the single byte fact
   `d1[2560+32*s+2] = 0`. The corollary establishes the marker from just the two inode-byte
   pins + the head name byte + the byte-region frame. Same conjunction the general intro builds,
   specialised to the empty name. Trigger UNCHANGED (`[dir_blit_marker d0 d1 s b0 b1 name]`).

2. **Standalone byte-fact materialisation before the fold** (the robust `_write_dir_entry`
   twin pattern). `_zero_entry`'s body now pre-proves EACH of the corollary's byte antecedents
   as its OWN cheap assert — crucially the **byte-region frame as a separate assert** — BEFORE
   the marker fold. This is the actual robustness lever: it pulls the expensive quantifier
   bridge OUT of the marker-establishment goal into its own isolated VC (exactly how
   `_write_dir_entry`'s committed 7→6 retirement stays robust), so the marker fold itself is
   cheap (~50K) and the frame is an isolated, deterministic goal.

(Option 2 "abstract helper carries the marker as a postcondition" was REJECTED: the marker is a
`self.dir`-field-referencing ensures, which does not propagate across the abstract-val boundary —
the documented method-call contract gap — which is exactly why `_blit_dir_entry` is
`sibling_concrete` / inlined. The marker MUST be established at the `_zero_entry` site.)

## FULL-GATE ×2 EVIDENCE (`_zero_entry` sub-goals — both runs IDENTICAL)

| sub-goal | run 1 | run 2 |
|---|---|---|
| Precondition | Valid 41766 | Valid 41766 |
| Assert: inode byte-pin b0 | Valid 4385 | Valid 4385 |
| Assert: inode byte-pin b1 | Valid 4386 | Valid 4386 |
| Assert: **byte-region frame** | **Valid 301358** | **Valid 301358** |
| Assert: head name byte / marker fold (intro_zero) | Valid 50342 | Valid 50342 |
| Assert: marker-keyed value+frame | Valid 51073 | Valid 51073 |
| Postcondition ×3 | Valid 51073/51991/52716 | Valid 51073/51991/52716 |

- `_zero_entry`: **0 non-Valid** in BOTH runs.
- The frame assert (301,358 steps) is the heaviest goal — **below** the v1 monolithic
  314K cost and well below `_write_dir_entry`'s robust committed 352K frame assert; **identical
  to the step across both runs** (deterministic robustness, margin to budget).
- The marker FOLD (formerly the monolithic 314K→Unknown step) is now a cheap **50,342-step**
  marker-keyed step.
- **Per-helper scan (both runs): zero_entry / write_dir_entry / blit_dir_entry / write_entry /
  dir_find_slot / dir_find_free / dir_lookup ALL 0 non-Valid** — no relocated explosion.
- **Only full-gate residual (both runs): `sys_rename` Assertion ×2 (Timeout)** — the
  pre-existing documented GAP (config/skills/pycsl-monitoring/SKILL.md §os: "sys_rename ×2
  Timeout"); unchanged by this work.

## FOUR GENUINENESS PROBES (on the FIXED de-trust, single-injection, --fun)

1. Consistency `#@ ensures 1 == 0` → **Unknown / RED** (the proof is not vacuously inconsistent). PASS
2. Value `slot_inode(self.dir,blk,slot)==0` → **Valid** (the live dead-slot postcondition, Valid in full gate). PASS
3. Value-falsification `==1` → **RED**. PASS
4. Frame falsification — off-by-one on a NON-mutated slot (`slot!=3 ⇒ slot_inode(.,5,3) CHANGED`,
   which the frame proves is preserved) → **RED**. PASS. (The naive "mutated-slot preserved"
   falsification is ill-posed via the `\old(self.dir)==self.dir` in-place-mutation collapse, as
   the mission notes; the off-by-one on a non-mutated slot is well-posed and falsifies.)

## NEW COROLLARY CROSS-VALIDATION (zero-TCB)

### Rocq (`0716.proofs/rocq/DirBlitMarker.v`) — `Print Assumptions` = Section Variables only

```coq
Theorem dir_blit_marker_intro_zero :
  forall (d0 d1 : disk) (s b0 b1 : Z) (nm : name_t),
    nlen nm = 0 ->
    rd d1 (slot_off 5 s) = b0 ->
    rd d1 (slot_off 5 s + 1) = b1 ->
    rd d1 (slot_off 5 s + 2) = 0 ->
    (forall b : Z, 0 <= b < 512 ->
        (b < 32 * s \/ 32 * s + 32 <= b) ->
        rd d1 (5 * 512 + b) = rd d0 (5 * 512 + b)) ->
    dir_blit_marker d0 d1 s b0 b1 nm.
Proof.
  intros d0 d1 s b0 b1 nm Hnl Hb0 Hb1 Hpad Hframe.
  unfold dir_blit_marker.
  repeat split.
  - rewrite Hnl. lia.
  - rewrite Hnl. lia.
  - exact Hb0.
  - exact Hb1.
  - intros i Hi. rewrite Hnl in Hi. lia.
  - intros i Hi. rewrite Hnl in Hi. lia.
  - intros _. rewrite Hnl. rewrite Z.add_0_r. exact Hpad.
  - intros b Hb Hout. apply Hframe; assumption.
Qed.
```

`coqc DirBlitMarker.v` → exit 0, no `Axiom`, no `Admitted`; `Print Assumptions
dir_blit_marker_intro_zero` prints only the Section Variables (`disk`, `rd`, `name_t`, `nchar`,
`nlen`) — Closed under the global context. Zero new TCB. (All 5 marker theorems in the file
remain Section-Variables-only.)

### Lean (`0716.proofs/lean/DirBlitMarker.lean`) — `#print axioms` ⊆ {propext, Quot.sound}

```lean
theorem dir_blit_marker_intro_zero (d0 d1 : Disk) (s b0 b1 : Int) (nm : Name)
    (hnl : nlen nm = 0)
    (hb0 : rd d1 (slot_off 5 s) = b0)
    (hb1 : rd d1 (slot_off 5 s + 1) = b1)
    (hpad : rd d1 (slot_off 5 s + 2) = 0)
    (hframe : ∀ b : Int, 0 ≤ b → b < 512 →
        (b < 32 * s ∨ 32 * s + 32 ≤ b) →
        rd d1 (5 * 512 + b) = rd d0 (5 * 512 + b)) :
    dir_blit_marker rd nchar nlen d0 d1 s b0 b1 nm := by
  refine ⟨?_, ?_, hb0, hb1, ?_, ?_, ?_, hframe⟩
  · rw [hnl]; omega
  · rw [hnl]; omega
  · intro i _ hi; rw [hnl] at hi; omega
  · intro i _ hi; rw [hnl] at hi; omega
  · intro _; rw [hnl]; simpa using hpad
```

`lean DirBlitMarker.lean` → exit 0, no `sorry`; `#print axioms dir_blit_marker_intro_zero` =
`'UnixFs.Dir.dir_blit_marker_intro_zero' depends on axioms: [propext, Quot.sound]` ⊆ the allowed
TCB bound.

### WhyML axiom (`src/pycsl/module6_whyml/preamble.py`)

```
"UnixFs.Dir.dir_blit_marker_intro_zero":
  forall d0 d1 : array int, s b0 b1 : int, name : string
  [dir_blit_marker d0 d1 s b0 b1 name].
  String.length name = 0 ->
  d1[2560 + 32 * s] = b0 -> d1[2560 + 32 * s + 1] = b1 ->
  d1[2560 + 32 * s + 2] = 0 ->
  ( forall b : int. 0 <= b < 512 ->
      (b < 32 * s \/ 32 * s + 32 <= b) -> d1[2560 + b] = d0[2560 + b] ) ->
  dir_blit_marker d0 d1 s b0 b1 name
```

Faithful 1:1 with the kernel theorem (trigger = the marker atom, unchanged). Emitted ONLY on
citation: cited by `_zero_entry`; NO corpus `.py` cites it.

## OTHER GATES

- **`__init__` gate** (`pycsl pure_lib/os/__init__.py`): SUCCESS, exit 0, **0 non-Valid** (216 Valid).
- **Corpus byte-diff**: emitted all 604 corpus `.mlw` under HEAD's preamble vs the modified
  preamble → `diff -rq` exit 0, **0 differences** (the new axiom is invisible to the corpus,
  emitted only on citation). The only corpus files touched are 0716's `.v`/`.lean` proof files,
  validated by direct compilation (above).
- **proof2why3 IR cross-check** (`crosscheck_ir UnixInodeFileSystem.py`): **0 FAIL** — the new
  `dir_blit_marker_intro_zero` citation resolves and is SKIP'd identically to all its sibling
  Dir marker axioms (parser-gap class, validated by the kernel proofs + documented
  correspondence), exit 0.
- **`\trusted` count**: HEAD 6 → proposal **5** (`_zero_entry`'s `#@ \trusted reviewer:
  dirscan-fidelity` removed). Remaining 5: `_dir_find_slot`, `_dir_find_free`, `_dir_lookup`,
  `_write_entry`, `_alloc_fd`(fd-resolution).

## DOC COHERENCY

No new directive surface (only a new cross-validated axiom NAME cited via the existing
`#@ proof` directive), so `bin/doc-coherency.py` is unaffected — no doc updates required.

## HUMAN SIGN-OFF NOTE

Adopting the new cross-validated axiom (`dir_blit_marker_intro_zero`) is a human-gated TCB
decision, not the monitor loop's. The axiom is kernel-PROVED (not bare `\trusted`), zero new TCB
in BOTH Rocq (Section-Variables-only) and Lean (⊆ {propext, Quot.sound}), and is a strict
specialisation of the already-trusted marker DEFINITION (the empty-name case of the existing
`dir_blit_marker_intro`). The parent should re-run the FULL body gate (×2) + the four probes +
recompile the Rocq/Lean before bringing it to the human. Nothing was committed; the working tree
is reverted to clean HEAD except this writeup and the v2 patch.
