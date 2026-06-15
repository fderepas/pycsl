# os API verification roadmap (living document)

**Purpose.** Track the path from the current state to a fully body-verified, functionally
faithful Python `os` API. This document EVOLVES — update the status table (§6) and the
milestone checkboxes (§5) as work lands. Companion plans: `14-string-field-codec-plan.md`
(the string/field-codec arc + §2.8–2.10 frame investigation).

Last updated: 2026-06-14 (after Layer-1 landed, commit `4cd0d0f`).

---

## 0. The two gates (read this first — they are constantly conflated)

| Gate | Command | What it proves | Status |
|---|---|---|---|
| **`__init__` gate** | `pycsl pure_lib/os/__init__.py` | the public `os.*` wrappers + pure helpers; emits each `sys_*` METHOD BODY as a TRUSTED `val` (body NOT verified here) | **GREEN** (committed deliverable) |
| **Body gate** | `pycsl pure_lib/os/UnixInodeFileSystem.py` | the actual `sys_*` METHOD BODIES against their contracts | ~94% Valid; heavy directory syscalls + content/readlink residual |

"Finishing the os API" = **the BODY gate proves every `sys_*` body** (so the `sys_*` contracts
the `__init__` gate trusts become PROVEN, not assumed), under the standing discipline (faithful
models, minimal TCB, `__init__` stays green, byte-diff clean).

A syscall is DONE when: its body proves in the body gate **and** its contract is a real
functional consequence (not a vacuous return-code echo — see [[feedback_formal_test_consequence]]).

---

## M4 PROGRESS 2026-06-14 (branch `m4-layer2-frame`, commit 1852322) — rmdir CLOSED; unlink/rename WALL
The A+B+C build landed on a BRANCH (not main — full body-gate regression unconfirmed in-session +
unlink/rename not closed). What works:
- **C** = `slots_lt32` class invariant (every block-5 slot's inode < 32) — definitional intro/elim
  like `uniq`. os `__init__` GREEN; established via `empty_disk_slots_dead`, maintained via
  `block5_decode_frame` + dir-mutator write-posts. (chmod OOMs WITH and WITHOUT C → C did not
  regress it; chmod was already a body-gate failure.)
- **A** = new `#@ propagate_frame` directive (wired Module2/3/5 like `sibling_concrete`) — opt-in
  per-callee propagation of a mutator's QUANTIFIED frame onto its boundary stub, pinned with a
  specific Call-trigger (fires on `slot_inode` only, never raw `self.disk[i]` → no §2.9 poison).
  Marked on `_zero_entry` (called only by unlink/rmdir/rename, never link/symlink).
- **RESULT:** `sys_rmdir` 1→**0 CLOSED**; `sys_rename` OOM→2 (improved); `sys_mkdir` 0→0;
  `sys_unlink` 1→1; `sys_link` 1→1; `sys_chmod` OOM→OOM (unchanged).
- **WALL (unlink/rename):** the absence assert needs the uniqueness step, but raw `uniq_elim`'s
  ∀i,j instantiation E-match-EXPLODES (13.7M steps), worsened by `slots_lt32_elim`.

### M4 ATTEMPT 2 2026-06-14 — `uniq_absent` lemma proves the PRE-zero absence but NOT the post-zero carry (reverted)
Added a definitional (zero-TCB) `UnixFs.Dir.uniq_absent` axiom — the FO consequence of
`uniq_elim`+`slots_lt32_elim`: in a uniq+slots_lt32 disk with slot s live, every other same-named
slot is dead — stated so SMT applies it O(1). FINDINGS:
- It **works for the PRE-zero (d1) absence**: with `uniq_absent` + the (B) slot-live loop-carry,
  the d1 absence assert PROVES (the uniqueness step is no longer the blocker).
- But the **POST-zero (d2) absence still explodes**: carrying the d1 absence through `_zero_entry`'s
  frame to the post-removal disk drowns in the FULL Dir-axiom set (block5 + scan_reflects +
  remove_reflects + the frame), even with the elims removed (9.7M steps). And `remove_reflects_absent`
  needs the absence on d2 (on d1 the name is still PRESENT), so d2 is unavoidable.
- `uniq_absent`, always-emitted with its broad `[uniq d, slot_name d 5 s]` trigger, **REGRESSED
  `sys_rename` 2→4** (fires for all 16 s). So it is net-harmful as a global axiom. REVERTED;
  branch stays at A+C (rmdir closed, 1852322).
- **REVISED FIX:** the intermediate-step route (prove absence, carry via frame) is E-matching-
  intractable in this dense context. The proper fix is ONE COMBINED cross-validated axiom
  `remove_unique_absent`: given uniq d0 + slot s the unique live `nm` entry + d1 = d0 with s zeroed
  (the `_zero_entry` byte-frame), conclude `dir_lookup(d1, nm) < 0` — the whole removal in a single
  O(1) application, no intermediate quantified asserts. Cross-validated Rocq+Lean (finite case
  split). That closes unlink/rmdir/rename uniformly. THE clean next step.
- Other merge prerequisites unchanged: full body-gate regression + `#@ propagate_frame` doc/corpus.

### M4 ATTEMPT 3 2026-06-14 — `remove_unique_absent` BUILT (correct) but the wall is STRUCTURAL, not a missing lemma (reverted)
Built `UnixFs.Dir.remove_unique_absent` as designed: a two-disk (pre/post-zero) lemma with a
`block5`-style multi-trigger `[slot_inode d1 5 s, slot_inode d0 5 s]`, concluding the post-zero
absence in O(1). It is mathematically correct (a FO consequence of `uniq_elim`+`slots_lt32_elim`+the
zero frame; zero-TCB definitional). FINDINGS — it still does NOT close unlink, and the ROOT CAUSE is
now definitive:
- The absence goal in unlink STILL times out (6.8M steps) WITH `remove_unique_absent` available,
  because the explosive `uniq_elim`/`slots_lt32_elim` (which unlink's free-blocks LOOP *needs* for
  `uniq` maintenance) are ALWAYS-EMITTED and the prover instantiates their ∀i,j / ∀k on unlink's
  many slot terms — exploding the search regardless of the O(1) lemma sitting right there.
- And like `uniq_absent`, `remove_unique_absent` as an always-emitted axiom REGRESSED `sys_rename`
  (2→3) via added E-matching noise — confirming: ANY always-emitted quantified directory axiom
  poisons some syscall in this dense context.
- **THE WALL IS STRUCTURAL: Why3 has no per-goal axiom scoping.** The absence proof needs the
  uniqueness FACT but is poisoned by the uniqueness ELIM that must be in scope (for the loop's
  maintenance). A correct lemma can't help because the prover still explores the explosive elims.
  Three mechanisms (Layer-2 frame, `uniq_absent`, `remove_unique_absent`) all hit this same wall.
- **REAL FIX (structural, beyond a lemma):** isolate the absence proof in a context WITHOUT the
  explosive elims — e.g. prove `remove_unique_absent` ONCE in a SEPARATE minimal Why3 theory/module
  (only `uniq`/`slots_lt32`/`slot_*` abstract, no os syscalls, no loop) and import it as an applied
  fact; OR an external (Rocq/Lean) proof imported as an opaque cited axiom that the os APPLIES
  without the elims competing. The key is removing `uniq_elim`/`slots_lt32_elim` from the os
  syscalls' VC context while keeping them where maintenance needs them — a Module6 emission change
  (scoped/cited elims), not just a new axiom. REVERTED attempt 3; branch stays at A+C (rmdir closed).
- **STATUS:** M4 = rmdir CLOSED; unlink/rmdir/rename's absence is blocked by this structural Why3
  limitation. Closing it needs the axiom-scoping/isolation work above — a larger Module6 change.
- **SPEC:** `15-0838-remove-unique-absent.md` specifies the fix — Part A: re-scope
  `uniq_elim`/`slots_lt32_elim` from always-emitted (`_CLASS_INV_AXIOMS`) to CITED-only (in the leaf
  writers, which gain `ensures uniq/slots_lt32` maintenance; the removers inherit it and stay
  elim-free); Part B: deliver `remove_unique_absent` as one applied fact (B1 cross-validated cited
  axiom — recommended; or B2 separate-theory zero-TCB lemma). A Module6 EMISSION change, not a new
  axiom.

## 1. The immediate mechanism: the 2-layer frame split

The heavy directory syscalls (unlink/rmdir/rename/symlink) fail in the body gate because a
`#@ no_inline` mutator's contract is DROPPED at the boundary stub (`self__zero_entry_<n>`
carried only `writes`). Restoring it splits cleanly into two layers by clause kind:

### Layer 1 — NON-QUANTIFIED write postconditions  ✅ DONE (`4cd0d0f`)
`slot_inode(self.disk,b,s)==inode` / `==0`, `self.x==v` — self-field + param, no `\result`/
`\old`/quantifier. Propagated via `_build_method_field_param_post_ensures_map`. Trigger-free ⇒
cannot E-match-poison. Result: **sys_unlink 3→1, sys_rmdir 2→1, sys_rename OOM→4-clean**;
`__init__` green; byte-diff 0; regression test `0710`.

### Layer 2 — QUANTIFIED frame, emitted PER-CALL-SITE  ⛔ NEXT (the real frame)
`\forall k≠s. slot_x(self.disk,5,k)==\old(slot_x(self.disk,5,k))`. This is the load-bearing
frame the absence/uniqueness asserts need. It CANNOT go on the shared stub — any usable trigger
fires on every `slot_*` term and OOMs rich callers (link/symlink; measured, §2.9). It must be
delivered **locally** at the one call site that needs it:
```
label PreCall in
self._zero_entry(5, slot)
#@ assume \forall k; (k <> slot) ==> slot_inode(self.disk,5,k) == (slot_inode(self.disk,5,k) at PreCall)
```
Build = a statement-level directive (`#@ assume` / `#@ frame_after`) + labeled-`assume` emission
with `at`-labels for the pre-call value + the language-audit (grammar→IR→WhyML, 5 doc surfaces,
corpus) + the uniqueness proof below. Sound because `_zero_entry` is `\trusted` (the frame is its
contract) and LOCAL (never enters link/symlink's context).

### Layer 2 also needs (the absence proof, independent of emission)
- `uniq_elim` instantiation: pre-state uniqueness (class invariant) + slot was the live `pathname`
  entry (`_dir_find_slot` ensures, now exposed by Layer 1) ⟹ no other live slot has `pathname`.
- a `slot_inode < 32` bound for the two slots uniq compares (where does it come from? — OPEN; may
  need a class-invariant clause `live ⇒ slot_inode<32` or a per-call assert).

### M4 DE-RISK RESULT 2026-06-14 — REACHABLE; needs A+B+C atomically (C is risky)
Manual `.mlw` probing on `sys_unlink` (`.audit-cache/m4/`) PROVED the absence assert (line 656,
`\forall k≠slot. slot_name(k)==pathname -> slot_inode(k)==0`) is dischargeable — `why3 prove` is
ALL VALID — GIVEN, on the pre-zero disk d1: (A) `_zero_entry`'s quantified frame, (B) `slot` live
+ named `pathname`, (C) `\forall i. slot_inode(disk,5,i) < 32`, plus the loop's `uniq`. Dropping
(C) → timeout (uniq's antecedent needs `slot_inode<32`). So all three are REQUIRED.
- **(A) frame** — Layer-2 emission. SAFE as a PER-CALLEE opt-in on `_zero_entry`: it is called ONLY
  by unlink/rmdir/rename, so its frame never enters link/symlink (the §2.9 poison was `_write_entry`'s
  frame). Buildable (per-callee flag, no full per-call-site machinery needed).
- **(B) slot-live@d1** — carry `slot_inode(slot)≠0 /\ slot_name(slot)==pathname` from `_dir_find_slot`
  (d0) through the free-blocks loop + post-loop writes to d1: strengthen the loop invariant (block5
  frame maintains it, exactly as it already maintains `uniq`) + post-write asserts. Moderate, in-body.
- **(C) `slot_inode<32`** — a NEW class invariant. NOT byte-derivable. Establish (empty disk → 0 via
  `empty_disk_slots_dead`) + maintain on every mutator (`_write_entry` sets `inode<32` from
  `_alloc_inode`; `_zero_entry` sets 0; non-block-5 writes preserve via block5_decode_frame). This
  is the LONG POLE — a directory-model change touching every method's type-invariant VC, RISKY to
  the green `__init__` (the `uniq` invariant took gaps 12–13). FLAGGED per [[feedback_safe_vs_risky_bricks]].
- **CAUTION:** adding (A) WITHOUT (B)+(C) makes unlink WORSE (1→2 timeouts — the frame is pure
  E-matching noise until the facts to use it exist). So A+B+C must land ATOMICALLY; no safe partial.
- **VERDICT:** M4 is reachable with a clear recipe, but it is the deep directory-absence rework (not
  just "emit the frame"). The gating risk is concentrated in (C). Probes saved in `.audit-cache/m4/`
  (unlink_max.mlw = the ALL-VALID witness).

---

## 2. Remaining work classes (what stands between us and 100% body gate)

| Class | Syscalls | Blocker | Plan |
|---|---|---|---|
| **A. Directory remove/rename** | unlink, rmdir, rename | Layer-2 frame + uniqueness (§1) | build Layer 2 |
| **B. Directory add** | mkdir ✅, link, symlink | link/symlink OOM on presence + EMLINK/alloc paths; need Layer-1 witness (have) + tame remaining E-matching | diagnose post-Layer-1 residual |
| **C. content round-trip** | write→read, pread | recover the data block value across calls (gap-17 effect contract) + the field codec | string-codec plan Phase C |
| **D. readlink target** | readlink, symlink target | return the decoded TARGET (today returns block #); needs `_pad_name` encode (have) + `field_to_str` decode (have) + cross-call framing | string-codec plan Phase C |
| **E. metadata/no-dir syscalls** | chmod, chown, utimensat, truncate, ftruncate, fstat, etc. | mostly proven via block5_decode_frame; scan residual | spot-fix residuals |
| **F. pure / fd-table syscalls** | open, close, dup, dup2, lseek, fsync, access, getdents, stat, lstat | largely proven (convergence-loop) | confirm 0 residual |

(Buckets per [[feedback_scope_pycsl_not_pure_lib]] / the stdlib-coverage skill's
modelled / specified / stubbed classification.)

---

## 3. Functional correctness (beyond structural safety)

Structural (bounds, type invariants, well-formed return codes) is largely done. The harder goal
is observable CONSEQUENCE through the PUBLIC API ([[feedback_test_calls_api]],
[[feedback_formal_test_consequence]]): mkdir→present, write→read-back, symlink→readlink-target,
rename moves the name, unlink→absent. These ride on Classes A–D above + the codec. The acceptance
target is `formal_0008.py` (the content round-trip, `\result == True`).

---

## 4. TCB / discipline (non-negotiable, every step)

- `__init__` gate stays GREEN; body gate only ever improves (scan EVERY non-Valid incl. "Out of
  memory" — [[os_gate_does_not_verify_method_bodies]]).
- corpus byte-diff via `bin/byte-diff-sweep.sh`; behavior change ⇒ corpus PROOF.
- new axioms: cross-validated Rocq+Lean OR zero-TCB definitional; no totalization, no value→int.
- new `#@` directive ⇒ full language audit (grammar→validate→IR→WhyML + 5 doc surfaces + corpus +
  faithful-lowering) — the Layer-2 `#@ assume`/`#@ frame_after` directive triggers this.

---

## 5. Milestones / sequencing

- [x] **M0** — `__init__` gate green; body gate measured (~94%).
- [x] **M1** — string-codec Phase A′ (field_to_str round-trip, cross-validated axiom).
- [x] **M2** — codec ENCODE side (`char_code_at`, `_pad_name` byte contract, end-to-end 0708).
- [x] **M3** — Layer-1 write-post propagation (unlink 3→1, rmdir 2→1).
- [ ] **M4** — Layer-2 per-call-site quantified frame + uniqueness ⇒ **close A (unlink/rmdir/rename)**.
- [ ] **M5** — diagnose + close **B** (link/symlink residual).
- [ ] **M6** — codec Phase C ⇒ **close C (content round-trip)** + **D (readlink target)**.
- [ ] **M7** — sweep **E + F** residuals to 0; body gate 100% Valid.
- [ ] **M8** — functional-correctness acceptance (`formal_0008.py`) through the public API.
- [ ] **M9** — retire trusted `sys_*` boundary in `__init__` (bodies now PROVEN) — the TCB shrink.

---

## 6. Live status table (update as we go)

Body-gate per-syscall unproven-goal counts (via `pycsl --fun unixinodefilesystem__<name>`).
Baseline = pre-Layer-1; "now" = current.

| syscall | baseline | now | blocker | milestone |
|---|---|---|---|---|
| sys_unlink | 3 | **1** | Layer-2 absence assert | M4 |
| sys_rmdir | 2 | **1** | Layer-2 absence assert | M4 |
| sys_rename | OOM | **4** | Layer-2 (both add+remove) | M4 |
| sys_mkdir | 0 | **0** ✅ | — | done |
| sys_link | 1 | 1 | presence/EMLINK residual | M5 |
| sys_symlink | OOM | OOM | presence + alloc residual | M5 |
| (others E/F) | — | mostly 0 | confirm | M7 |

(Refresh this table after each milestone; record the exact failing goal per remaining syscall.)
