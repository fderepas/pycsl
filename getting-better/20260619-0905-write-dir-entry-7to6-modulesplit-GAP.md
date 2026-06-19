# `_write_dir_entry` 7→6 retirement — MODULE-SPLIT / axiom-narrowing follow-on: GAP

DATE: 2026-06-19
LOOP: test-supervise-sl (mission: overcome the route-1 catalog-B A.7 aggregate-context wall by
verifying the dir mutators against a DELIBERATELY SMALLER axiom set — a sound module split /
axiom-scope narrowing via Track-B opacity — so the `_write_dir_entry` de-trust gates green in the
FULL verification → `\trusted` 7→6. STOP AT THE PROPOSAL.)

STATUS: **DOES NOT RETIRE — and the module-split premise is REFUTED as the mechanism.** The mission
framed the wall as "too many axioms in scope at the `_write_dir_entry` VC." I measured this directly
and it is **not** the mechanism: the axiom scope at that VC is byte-IDENTICAL between `--fun` (where
the function PROVES) and the full file (where it OOMs). Narrowing the cited axioms — even down to a
9-axiom minimal set — does **not** close the two frame postconditions; only the `--fun` configuration
(every sibling trusted, ZERO self-call stubs) proves them. A sound Why3 `scope` boundary that would
reproduce the `--fun`-lean context for `_write_dir_entry` inside the full module is architecturally
possible (Why3 scope axiom-isolation verified) but is **NOT implemented in PyCSL** (the emitter
produces one flat `module PyCSL_Program`, no scope/module machinery) and, more importantly, the
lean context that actually works is as aggressive as `--fun` — a major emitter feature, human-gated.
Tree reverted to clean HEAD; the route-1 marker proofs RE-CONFIRMED zero-TCB both provers (banked,
eligible). No v3 de-trust/split is left in the tree because **no working split was achieved**.

## Bottom line (the mission questions)

1. **Does it NOW retire 7→6, both gates green, soundness probe clean, boundary PROVEN not trusted?
   NO.** The `_write_dir_entry` `\trusted reviewer: dirscan-fidelity` removal is syntactic 7→6, but
   the two `∀k≠slot` frame postconditions OOM/Timeout in the full module under every narrowing I
   could construct. No sound boundary closes it this session.

2. **Is the wall "too many axioms in scope"? NO — REFUTED.** Measured: the emitted axiom set, the
   predicate/function declarations, and the `_write_dir_entry` `let` body are ALL byte-identical
   between the full emission (15 axioms) and `--fun` (15 axioms). `--fun` works by trusting every
   OTHER function (emit as `val`), which is what removes the self-call-stub apparatus — NOT by
   changing the axiom scope. The axioms are red herrings; the real variable is the rest of the
   module's `let`/stub apparatus being present in the proving session.

3. **Is the route-1 marker cross-validated zero-TCB? YES (RE-CONFIRMED this run).**
   `coqc DirBlitMarker.v` → exit 0, `Print Assumptions` = Section Variables only, no Axiom/Admitted.
   `lean DirBlitMarker.lean` → exit 0; `dir_blit_marker_intro` depends on NO axioms;
   `dir_blit_marker_insert` depends on `[propext, Quot.sound]`; no sorry.

4. **The precise residual:** the two frame postconditions of `_write_dir_entry`
   (`∀k≠slot. slot_inode self.dir 5 k == \old(...)` and the slot_name twin) OOM/Timeout in the full
   module regardless of axiom narrowing. They prove ONLY when the entire rest of the module is
   trusted away (`--fun`). This is a VC-context (E-graph apparatus) wall, not an axiom-scope wall.

## What I measured (the decisive experiments)

All in a scratch worktree (`git worktree`, HEAD + `PROPOSAL-write-dir-entry-detrust-v2.patch`),
PYTHONHASHSEED=0, Alt-Ergo 2.6.x + Z3, `-a split_vc`, per-goal isolation via
`why3 prove ... -T PyCSL_Program -G "unixinodefilesystem___write_dir_entry'vc"`.

### Architecture facts
- PyCSL emits the ENTIRE os module as ONE Why3 `module PyCSL_Program` (1..1889). No `scope`, no
  multi-module, no `clone`. A flat theory: every `axiom` is in scope for every `let`/`goal`.
- `_emit_preamble_axioms` (preamble.py ~1747) scans EVERY function's `#@ proof` entries and emits each
  cited axiom once, module-globally. `_emit_class_inv_axioms` emits the uniq/slots_lt32 maintenance
  axioms before the record, also module-global.

### `--fun` vs full = IDENTICAL axiom scope (the refutation)
- `--fun X` marks all OTHER functions `\trusted` (emit as `val`) — pycsl.py:484-488.
- Emitted axioms: full = 15, `--fun` = 15 — `diff` of the names = IDENTICAL.
- predicate/function decls = IDENTICAL.
- `_write_dir_entry` `let` block = BYTE-IDENTICAL (full vs `--fun`).
- ⇒ The axiom scope at the failing VC is the SAME in both. The mission premise is not the mechanism.

### Goal-isolated from the FULL module (all 15 axioms, all sibling `let`s present):
- slot_inode VALUE postcond: Valid (~50K steps); slot_name VALUE postcond: Valid; marker asserts: Valid.
- **slot_inode FRAME: Out of memory (8.86s) [Z3] / Timeout (Alt-Ergo)**
- **slot_name  FRAME: Timeout 5.46M steps [Z3] / Timeout (Alt-Ergo)**
- Confirmed both provers individually at 60s: frame goals Timeout 329247 / 452958 (Alt-Ergo),
  OOM / Timeout 8.0M (Z3).

### `--fun` (everything else trusted; 0 self-call stubs; 15 axioms): SUCCESS, frames Valid
- Re-run captured: all sub-goals Valid, frame goals ~48275 / 48639 steps. `[+] Verification SUCCESS`.

### Axiom narrowing in the emitted .mlw (hand-edited): INSUFFICIENT
- Remove the 4 read-side dir axioms (scan_reflects_present, remove_reflects_absent,
  remove_unique_absent, dir_lookup_frame): the marker assertion improves and the VALUE postconds stay
  Valid, but the **two FRAME postconds still fail** (Z3 Unknown 376826 / OOM; Alt-Ergo Timeout
  108794 / 114395 — and at 60s: Timeout 301965 / 459522).
- Remove 6 axioms (also establish_uniq/establish_slots_lt32, → 9 axioms): the marker assertion now
  proves under best-of-N, but the **two FRAME postconds STILL fail both provers** (Z3 Unknown 376826 /
  OOM; Alt-Ergo Timeout).

### Inlining lever (drop `#@ sibling_concrete` on `_blit_dir_entry`, helper as abstract `val`): INSUFFICIENT
- With the helper a clean `val` AND all 15 axioms: the marker INTRO asserts go Unknown (byte-frame
  antecedent unmet, as expected), VALUE postconds Valid, and the **two FRAME postconds STILL fail**
  (Z3 OOM / Timeout 11.8M; Alt-Ergo Timeout 181344 / 173320).

### Self-call-stub lever: the stubs are USED by siblings → cannot be deleted; stripping their ensures
  (keeping the decl) leaves the FRAME postconds FAILING identically (Z3 OOM / 11.8M; Alt-Ergo
  Timeout 200328 / 175071). So the stub *ensures* are not the pollutant either.

### Why3 scope axiom-isolation: VERIFIED SOUND (the tool a real split would use)
Minimal Why3 test: two sibling `scope`s with contradictory axioms each prove their own goal in
isolation (`g_lean: f 0 = 1` from `lean_ax`; `g_sib: f 0 = 2` from `sibling_ax`); a goal outside both
sees neither. Cross-scope call (`Sibling.caller` calling `Lean.wde`) typechecks. So Why3 *can* express
a sound boundary — but PyCSL does not emit scopes, and the lean context that actually proves the frames
is as aggressive as `--fun` (essentially every sibling + the read-side dir axioms hidden), not just
the 4–6 dir axioms.

## Gate evidence (authoritative, PYTHONHASHSEED=0, best-of-N)
- **BASELINE (clean HEAD, `_write_dir_entry` trusted): 2 goals remain** — both `sys_rename`
  Assertion Timeout (4621194 / 243097 steps). 7 `\trusted reviewer: dirscan-fidelity` (= 7 total).
- **DE-TRUSTED full body gate (v2 patch):** does NOT complete in 590s (EXIT 124) — the de-trust makes
  the file's proving so slow (the frame OOMs each cost ~10–17s × 2 provers × many goals) that it does
  not finish in ~10 min. The route-1 residual stands: `_write_dir_entry` frame Postcondition ×2 +
  sys_rename baseline = a body-gate REGRESSION (frames never Valid). NOT ≤ baseline.
- **`\trusted`:** HEAD os = 7; de-trusted = 6 SYNTACTICALLY, but the body reds ⇒ does NOT retire.
- **`__init__` / corpus byte-diff:** not run — the body gate already fails decisively (retirement
  dead at the body gate). The marker axioms remain emission-gated/uncited-elsewhere (corpus-inert).

## Why the module split does NOT close it (the honest mechanism)
The A.7 label ("too many axioms in scope") is INACCURATE for this VC: the cited axioms are not the
driver. The two `∀k≠slot ... \old(...)` frame postconditions are at the feasibility edge for both
SMT solvers, and they tip into OOM/Timeout in the presence of the full module's *program apparatus*
(the 60 sibling `let` bodies and the 17 abstract self-call stubs that all reference
`slot_inode`/`slot_name`/`dir_lookup`), independent of the `#@ proof` axiom set. Only `--fun` —
which removes that apparatus by trusting every sibling — proves them. A sound boundary would have to
reproduce that lean context for `_write_dir_entry` while still verifying the siblings elsewhere. Why3
`scope` can do this in principle, but:
- PyCSL has no scope/module emission — building it is a substantial, high-blast-radius emitter feature.
- The lean context that works is essentially "hide everything but the marker axioms + the clean blit
  `val`," not a small axiom subset — so the scope would be very aggressive, and proving the SIBLINGS
  (which genuinely need scan_reflects_present etc. AND a verified `_write_dir_entry` contract) in the
  outer scope must still go green with the lean `_write_dir_entry` exposed only by its proven
  postcondition. That cross-scope soundness is the architectural work, human-gated.

This is doctrine-clean: NO `\trusted` was added, NO contract weakened, NO trigger widened. The marker
is banked and cross-validated. The retirement stays a LOGGED GAP routed to the human — now with a
sharper diagnosis (apparatus-context, not axiom-scope) and a concrete (but un-built) sound mechanism
(PyCSL scope emission reproducing the `--fun`-lean context).

## What a future session / the human needs (NOT autonomous — architecture + TCB sign-off)
1. **PyCSL scope/module emission** (the real "module split"): emit `_write_dir_entry` (+ `_blit_dir_entry`
   as a clean abstract `val`) and the marker axioms in a lean Why3 `scope`; emit the rest (sys_*,
   `_dir_lookup`, the self-call stubs, the read-side dir axioms) in the outer module that `use`s the
   lean scope's PROVEN `_write_dir_entry` contract. Why3 scope axiom-isolation is verified sound; the
   boundary is a PROVEN interface (the lean scope fully discharges the body), not a trust. Measure that
   the lean context is lean ENOUGH (the frames need ~`--fun`-level leanness) AND the outer scope still
   greens with NO new unproven anywhere (watch the wall relocating to a sibling/consumer).
2. Alternatively: investigate a Why3 trigger/weight or `meta` directive that makes the two frame
   postconditions feasible in the full apparatus without a scope split (lower-blast, but uncertain).

## Cross-validation outputs (verbatim, RE-CONFIRMED this run)
```
# Rocq — coqc DirBlitMarker.v: exit 0
#   Print Assumptions dir_blit_marker_intro / dir_blit_marker_insert: Section Variables only
#   (name_t : Type; disk : Type; rd/nlen/nchar). No Admitted, no Axiom.
# Lean — lean DirBlitMarker.lean: exit 0, no sorry
#   'UnixFs.Dir.dir_blit_marker_intro'  does not depend on any axioms
#   'UnixFs.Dir.dir_blit_marker_insert' depends on axioms: [propext, Quot.sound]
```

## Patch + reproduction
- The route-1 de-trust (unchanged, the substrate I probed): `getting-better/PROPOSAL-write-dir-entry-detrust-v2.patch`
  (`git apply` on clean HEAD; marker registry + predicate + de-trust + direct-write `_blit_dir_entry`
  + `0716.proofs/{rocq,lean}/DirBlitMarker.{v,lean}`). Re-applies cleanly; produces the green-`--fun`
  / red-full-gate state documented here.
- **No v3 module-split patch is produced — no working split was achieved.** The deliverable is this
  GAP write-up + the re-confirmed banked marker. Producing a v3 patch would require first BUILDING the
  PyCSL scope-emission feature, which is the human-gated architecture decision itself.

## STOP-AT-PROPOSAL
Per the standing instruction: nothing committed, nothing left in the tree. The scratch worktree was
removed; the main tree is at clean HEAD (only this GAP doc is new). The marker proofs are banked +
cross-validated; the retirement remains an honest LOGGED GAP with a corrected diagnosis: the wall is
APPARATUS-context feasibility of two frame postconditions, not axiom scope — and the doctrine-clean
close is a PyCSL scope-emission module split reproducing the `--fun`-lean context, a human
architecture + TCB sign-off decision.
