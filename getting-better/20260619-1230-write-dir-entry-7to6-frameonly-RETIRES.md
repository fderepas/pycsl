# `_write_dir_entry` 7→6 retirement — RETIRES on the v3 (vacuity-repaired) substrate via the `frame_only` corollary

DATE: 2026-06-19
LOOP: test-supervise-sl (mission: on the REPAIRED v3 substrate, re-test Spike-2's `frame_only`
axiom and, if genuine, assemble the full `_write_dir_entry` 7→6 retirement. STOP AT PROPOSAL.)
STATUS: **RETIRES.** On the SOUND v3 substrate, the cross-validated zero-TCB `frame_only`
corollary closes both `∀k≠slot` frame postconditions of `_write_dir_entry` in the FULL body
gate, GENUINELY (all four full-module probes clean), with NO relocated explosion, residual
≤ baseline (in fact 2→1), `__init__` gate GREEN, and ZERO corpus byte-diff beyond the os
module. This is the FIRST dirscan-fidelity `\trusted` retirement and adds a NEW emitted axiom a
live trust depends on — **pending human TCB sign-off** (the parent re-verifies before sign-off).

## 1. BOTTOM LINE (the mission questions)
1. **Retires 7→6, full body gate green?** YES. `#@ \trusted reviewer: dirscan-fidelity` on
   `_write_dir_entry` is removed (file `\trusted` count 7→6). The full body gate residual goes
   from **2 → 1** (a strict improvement), and the single remaining residual is the SAME
   pre-existing `sys_rename` assertion present at baseline.
2. **All four FULL-module genuineness probes clean?** YES (§4). Consistency Unknown; genuine
   value Valid; wrong-value RED; frames Valid + wrong-slot RED — all in the FULL module with
   `frame_only` emitted.
3. **Byte-diff only-os?** YES (§5). v3-vs-v3+`frame_only` corpus byte-diff = **0** across all 604
   corpus `.mlw`. The new axiom is emission-gated (cited only by `_write_dir_entry`), so it
   appears ONLY in the os module's `.mlw` (`UnixInodeFileSystem.mlw` + `__init__.mlw`).
4. **No relocated explosion?** YES. Every dir mutator (`_write_dir_entry`, `_blit_dir_entry`,
   `_zero_entry`, `_write_entry`) is fully Valid; the prior route-1 `_blit_dir_entry` 869M-step
   explosion does NOT reappear (the marker-keyed trigger never matches a raw `disk[2560+...]`).

## 2. THE `frame_only` AXIOM (the cross-validated, zero-TCB deliverable)

Added to `src/pycsl/module6_whyml/preamble.py` `_AXIOM_REGISTRY` (emission-gated; same
`#@ proof` citation pattern + in-code doc pattern as the other `dir_blit_marker_*`):

```
UnixFs.Dir.dir_blit_marker_frame_only :
  forall d0 d1 : array int, s b0 b1 : int, name : string [dir_blit_marker d0 d1 s b0 b1 name].
    dir_blit_marker d0 d1 s b0 b1 name ->
    0 <= s < 16 ->
    ( forall k : int. 0 <= k < 16 -> k <> s ->
        slot_inode d1 5 k = slot_inode d0 5 k /\
        slot_name  d1 5 k = slot_name  d0 5 k )
```

It is **`slot_frame_of_region` applied to the marker definition's byte-region-frame conjunct**:
the SLOT-LOCALITY FRAME alone, needing ONLY the marker (= the byte facts, by definition) and the
slot-in-range fact — NOT uniq/slots_lt32/inode-range/freshness. Marker-keyed trigger
`[dir_blit_marker d0 d1 s b0 b1 name]` (identical key to `intro`/`insert`), so it CANNOT match a
bare `disk[2560+<expr>]` byte read — never poisons `_blit_dir_entry` or any block-5 toucher.

### Why it is a STRICT corollary of the v3 `dir_blit_marker_insert` (zero new TCB)
`dir_blit_marker_insert` ALREADY derives this exact frame conjunct as its sub-result `Hsf`/`hsf`
— purely from the marker's frame component via `slot_frame_of_region`, BEFORE and INDEPENDENT of
the value/uniq/slots_lt32/freshness reasoning. `frame_only` is that same sub-derivation exposed
as its own theorem (destruct the marker, apply `slot_frame_of_region`). v3 narrowed the insert's
freshness antecedent to `k<>s`; `frame_only` does not reference freshness at all, so the v3
narrowing is irrelevant to it — it is a strict consequence of the marker DEFINITION (hence of any
axiom, incl. the v3 insert, that conservatively defines the marker by its byte facts).

### Re-cross-validation (verbatim, this run; recompiled against the v3 sources)
`test-suite/corpus/pycsl-reference/0716.proofs/{rocq,lean}/DirBlitMarker.{v,lean}`, the v3 proof
files with `dir_blit_marker_frame_only` added after `dir_blit_marker_insert`:

```
# Rocq 8.20.1 — coqc DirBlitMarker.v — Print Assumptions dir_blit_marker_frame_only:
Section Variables:
rd    : disk -> Z -> Z
nlen  : name_t -> Z
nchar : name_t -> Z -> Z
name_t : Type
disk   : Type
   (Closed under the global context — 0 Axiom / 0 Admitted; same as intro/insert)

# Lean 4.31.0 — lean DirBlitMarker.lean — #print axioms:
'UnixFs.Dir.dir_blit_marker_intro'      does not depend on any axioms
'UnixFs.Dir.dir_blit_marker_insert'     depends on axioms: [propext, Quot.sound]
'UnixFs.Dir.dir_blit_marker_frame_only' depends on axioms: [propext, Quot.sound]   (⊆ allowlist)
```

Rocq corollary (the whole proof body):
```
Theorem dir_blit_marker_frame_only :
  forall (d0 d1 : disk) (s b0 b1 : Z) (nm : name_t),
    dir_blit_marker d0 d1 s b0 b1 nm ->
    0 <= s < 16 ->
    forall k : Z, 0 <= k < 16 -> k <> s ->
      slot_inode d1 5 k = slot_inode d0 5 k /\
      slot_name  d1 5 k = slot_name  d0 5 k.
Proof.
  intros d0 d1 s b0 b1 nm Hmark Hs.
  destruct Hmark as [_ [_ [_ [_ [_ [_ [_ Hframe]]]]]]].
  exact (slot_frame_of_region d0 d1 s Hs Hframe).
Qed.
```
Lean corollary:
```
theorem dir_blit_marker_frame_only (d0 d1 : Disk) (s b0 b1 : Int) (nm : Name)
    (hmark : dir_blit_marker rd nchar nlen d0 d1 s b0 b1 nm)
    (hs0 : 0 ≤ s) (hs1 : s < 16) :
    ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s →
      slot_inode rd d1 5 k = slot_inode rd d0 5 k ∧
      slot_name rd d1 5 k = slot_name rd d0 5 k := by
  obtain ⟨_, _, _, _, _, _, _, hframe⟩ := hmark
  exact slot_frame_of_region rd d0 d1 s hs0 hs1 hframe
```

## 3. FULL BODY GATE — before / after (PYTHONHASHSEED=0, best-of-N Alt-Ergo 2.6.2 + Z3 4.13.3, 30s/goal)

`PYTHONHASHSEED=0 .venv/bin/python3 src/pycsl/pycsl.py pure_lib/os/UnixInodeFileSystem.py`
(verdict grep includes "Out of memory" per the os-gate blind-spot discipline):

| build | `_write_dir_entry` | Valid / total | residual (non-Valid) |
|-------|--------------------|---------------|----------------------|
| **BASELINE** (clean HEAD, `_write_dir_entry` `\trusted`) | emitted as trusted `val` (0 body goals) | 896 / 900 | **2** — both `sys_rename` Assertion **Timeout** (30s; 4.62M / 248K steps), SAME goal char-range `21-111` |
| **v3 + `frame_only`** (de-trusted) | verified `let`, **10 goals ALL Valid** (4 Postcondition = value×2 + frame×2; 5 Assertion; 1 Precondition) | 935 / 936 | **1** — `sys_rename` Assertion **OOM** (20.6s), SAME goal char-range `21-111` |

- The de-trust adds `_write_dir_entry`'s 10 genuine goals (all Valid) and REMOVES one residual:
  2→1. The remaining residual is the SAME pre-existing `sys_rename` reconciliation assertion
  (`(slot_inode self.dir 5 !old_slot <> 0) && (slot_name self.dir 5 !old_slot = oldpath)` — the
  oldpath-absence-survives-newpath-write step), at the identical mlw char-range `21-111` in both
  builds; Timeout at baseline / OOM here is prover non-determinism on the SAME unproven goal. It
  is NOT a `_write_dir_entry` goal, NOT a frame goal, and NOT introduced by `frame_only`.

### Per-mutator VC scan (the explosion must not relocate) — ALL Valid in the v3+`frame_only` gate
- `_write_dir_entry` — 10 goals, all Valid (incl. the two `∀k≠slot` frame Postconditions).
- `_blit_dir_entry` — all goals Valid (the prior route-1 869M-step explosion site; clean here).
- `_zero_entry` — all goals Valid.
- `_write_entry` — all goals Valid.

## 4. FULL-MODULE GENUINENESS — all four probes, in the FULL gate with `frame_only` emitted

| # | probe | construction (full module) | result |
|---|-------|----------------------------|--------|
| 1 | **Consistency** | `#@ assert (inode_num != 0 and inode_num < 32) ==> 1 == 0` after the marker assert | **Unknown / Timeout** (Alt-Ergo Unknown 0.54s/379K; Z3 Timeout 30s/94K) — live branch CONSISTENT, NOT vacuous; all other `_write_dir_entry` goals stay Valid |
| 2 | **Genuine value** | real `slot_inode==inode_num` + `slot_name==name` ensures | **Valid** (the 4 genuine Postconditions in the §3 green gate) |
| 3 | **Wrong value (falsification)** | extra ensures `slot_inode(...,slot)==inode_num + 1` | **RED** (Timeout 22.6s/8.9M; mlw line 1028) — proves (2) is real |
| 4 | **Frames + wrong-slot** | genuine `∀k≠slot` frames Valid; extra ensures `∀k≠slot. slot_name(...)==name` | frames **Valid**; wrong-slot frame **RED** (OOM 27.6s; mlw line 1029) |

In probe 3+4 the 2 false ensures are the ONLY new non-Valid `_write_dir_entry` Postconditions
(adjacent mlw lines 1028/1029); the 4 genuine Postconditions remain Valid — so the genuine
value/frames are non-vacuous.

## 5. BYTE-DIFF (corpus) — only-os confirmed

Parallel `--no-typecheck` emission sweeps (604 corpus `.mlw` each):
- **v3-only** (frame_only registry entry removed) **vs v3 + `frame_only`**: `diff -rq` = **0 files
  differ.** `dir_blit_marker_frame_only` does NOT appear in ANY corpus `.mlw` (emission-gated;
  corpus never cites it). The os codec exhibits 0711/0712 are byte-identical between the two.
- (For reference, the v3 substrate itself adds ONE line to 0711/0712 — the `dir_blit_marker`
  predicate DECLARATION pulled in by the `UnixFs.Dir.` axiom block — but that is the GIVEN v3
  substrate, not this run's `frame_only` delta.)

## 6. OTHER GATES
- **`__init__` gate GREEN:** `pure_lib/os/__init__.py` → **216 Valid / 216 total**, "Verification
  SUCCESS! All contracts formally proven", exit 0, ZERO non-Valid (no relocated OOM). `frame_only`
  is present in `__init__.mlw` (via the `UnixInodeFileSystem` import that cites it) and does not
  poison any wrapper/constructor VC. (Note: the mission's "1182/0" figure predates this HEAD;
  the actual `__init__` gate here is 216/0 — fully green is the load-bearing fact.)
- **`\trusted` 7→6:** `_write_dir_entry`'s `#@ \trusted reviewer: dirscan-fidelity` removed; file
  `\trusted` count 6 (5 dirscan-fidelity + 1 fd-resolution-fidelity).
- **doc-coherency `--check`:** PASS (51 directives in sync; no new `#@` directive — the new
  registry axiom is internal preamble, documented via the in-code `dir_blit_marker_*` doc pattern).
- **Typecheck:** `--no-proof` on `UnixInodeFileSystem.py` → L3-tc ✓ (the `frame_only` WhyML axiom
  is well-formed).

## 7. DELIVERABLES
- `getting-better/PROPOSAL-write-dir-entry-detrust-v4-frameonly.patch` — self-contained superset
  of v3: the marker registry + predicate + de-trust + direct-write `_blit_dir_entry` + the v3
  freshness `k≠s` repair + **the `frame_only` registry entry + citation** + the re-cross-validated
  0716 proof sources (with the `frame_only` corollary). `git apply` from repo root, applies clean
  on HEAD.

## 8. HUMAN-TCB SIGN-OFF NOTE (BINDING)
This is the FIRST `dirscan-fidelity` `\trusted` retirement. It works by ADDING a NEW emitted,
cross-validated axiom (`dir_blit_marker_frame_only`) that a LIVE os trust (`_write_dir_entry`'s
de-trusted frame postconditions) depends on. Per doctrine that is a HUMAN TCB decision — the
user's explicit sign-off — NEVER the loop's or the parent's to ship autonomously. The de-trust is
NOT left in the tree. The parent re-applies the v4 patch, recompiles `frame_only` (re-checks
`Print Assumptions`/`#print axioms`), and re-runs the full-module four-probe genuineness + the
body/`__init__` gates before bringing the retirement to the human.

## 9. TREE STATE
Reverted to clean HEAD. `git diff HEAD` empty except the two new files under `getting-better/`
(the v4 patch + this writeup); stash empty; corpus/`.mlw`/coq/lean build artifacts cleaned.
