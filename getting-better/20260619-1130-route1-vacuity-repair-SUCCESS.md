# Route-1 `_write_dir_entry` de-trust — LIVE-BRANCH VACUITY: REPAIRED (v3)

DATE: 2026-06-19
LOOP: test-supervise-sl (mission: REPAIR the confirmed live-inode-branch vacuity in the
route-1 `_write_dir_entry` de-trust substrate captured in
`getting-better/PROPOSAL-write-dir-entry-detrust-v2.patch`).
STATUS: **REPAIRED.** All four genuineness-bar items hold at `--fun` level on BOTH the
canonical (empty) disk AND a populated soundness-probe disk. The marker axiom change is
re-cross-validated zero-TCB in BOTH Rocq and Lean.

## 1. ROOT CAUSE

The live-inode branch was inconsistent because of an **`\old`-vs-post-state collapse** that
degenerated the directory-blit marker into a self-referential (reflexive) instance, where the
**over-strong all-`k` freshness antecedent** then contradicted the inserted slot's own value.

### Localization (guarded `->false` probe, walked down the body)
Inserting `#@ assert (inode_num != 0 and inode_num < 32) ==> 1 == 0` after each step of
`_write_dir_entry`:
- after `_blit_dir_entry` call .................... probe **Unknown** (consistent)
- after the inode-byte assert ..................... probe **Unknown**
- after the name-byte / null-pad asserts .......... probe **Unknown**
- after the byte-region frame assert .............. probe **Unknown**
- **after the `dir_blit_marker(...)` assert ....... probe VALID (inconsistent)**

So the inconsistency is introduced EXACTLY by the marker assert
(`pure_lib/os/UnixInodeFileSystem.py`, the `#@ assert dir_blit_marker(\old(self.dir),
self.dir, slot, ...)` line in `_write_dir_entry`).

### Trigger-set bisection (necessary-and-sufficient)
Editing `dir_blit_marker_insert`'s conclusion (`src/pycsl/module6_whyml/preamble.py`):
- drop `slot_name d1 5 s = name` ............... probe Unknown → that conclusion is required
- drop the `∀k≠s` frame and `uniq/slots_lt32` .. probe STILL Valid → frame NOT required
- keep ONLY `slot_inode d1 5 s = 256*b0+b1 ∧ slot_name d1 5 s = name` .. probe Valid →
  the TWO VALUE decodes TOGETHER are the conclusion side of the contradiction.
Disabling the function's freshness `requires` ..... probe Unknown → **freshness is required.**

### The mechanism (confirmed by the alt-ergo Tableaux unsat core, 987 steps)
The unsat core for the `1=0` goal contains, decisively, the manufactured atom
`dir_blit_marker (dir self) (dir self) slot b0 b1 name` — i.e. **d0 = d1 = `(dir self)`**.
`_blit_dir_entry` is an opaque `val` that mutates the `mutable dir : array int` record field
**in place** (no `writes`/fresh-array reframing exists anywhere in the emitted `.mlw`), so in
the post-state VC `\old(self.dir)` and `self.dir` resolve to the SAME array term `(dir self)`.
The body's `#@ assert dir_blit_marker(\old(self.dir), self.dir, ...)` therefore asserts a
**reflexive** marker. The intro axiom (definitional, bytes→marker) is also free to manufacture
the reflexive marker directly from `(dir self)`'s own bytes.

`dir_blit_marker_insert` then fires on this `d0=d1=(dir self)` marker:
- value: `slot_inode (dir self) 5 slot = inode_num`, `slot_name (dir self) 5 slot = name`
  (the genuine post-state facts), with the live guard giving `0 < inode_num < 32`.
- **freshness antecedent over `d0 = (dir self)` (the post-state):**
  `∀k. live(k) → slot_name (dir self) 5 k ≠ name`. The function's freshness `requires` —
  legitimately written over `self.dir` (pre-state in Python semantics) — collapses to the
  SAME `(dir self)` term and supplies exactly this. **At k = slot**, the slot is now live
  with `slot_name (dir self) 5 slot = name`, so the antecedent forces `name ≠ name` = **False**.

The genuine postconditions (`slot_inode/slot_name` value + frame) are NOT the problem and were
NEVER weakened. The bug is the **all-`k` freshness over-constraint**: it includes the very slot
`s` that the insert overwrites, which is semantically irrelevant to duplicate-creation but,
under the `\old==post` array-aliasing collapse, makes freshness self-contradict the insert's
own value conclusion.

## 2. THE REPAIR (sound, minimal, zero-TCB)

Restrict the freshness antecedent to slots **other than the target slot `s`** — in BOTH the
`dir_blit_marker_insert` axiom AND the function's freshness `requires`:

- `src/pycsl/module6_whyml/preamble.py` (`dir_blit_marker_insert`):
  `( forall k. 0 <= k < 16 -> slot_inode d0 5 k <> 0 -> ... -> slot_name d0 5 k <> name )`
  → `( forall k. 0 <= k < 16 -> k <> s -> slot_inode d0 5 k <> 0 -> ... -> slot_name d0 5 k <> name )`
- `pure_lib/os/UnixInodeFileSystem.py` (`_write_dir_entry` freshness `requires`): add `k != slot`.

**Why this is SOUND, not a doctrine-forbidden weakening of the proven property:**
- The genuine value/frame POSTCONDITIONS (the properties being proven) are UNCHANGED and prove
  GENUINELY (falsification-confirmed below). What changed is a *supporting hypothesis* of the
  maintenance axiom.
- The all-`k` freshness was OVER-STRONG: a fresh-name single-slot insert at `s` cannot
  manufacture a duplicate live-name pair as long as `name` is not already live at some slot
  **other than `s`**. Whether `s` itself held `name` pre-write is irrelevant — `s` is
  overwritten. So the `k≠s`-restricted antecedent is the faithful uniqueness-maintenance
  precondition.
- The cross-validated Rocq/Lean theorems ALREADY only ever apply freshness at slots `≠ s`
  (DirBlitMarker.v: `Hfresh j`/`Hfresh i` are reached only after `subst i`/`subst j`, i.e. the
  OTHER index, which carries `<> s`; Lean identically). Adding the `k ≠ s` hypothesis to
  `hfresh` is therefore the SAME proof with an unused premise narrowed — no new TCB.
- The function precondition becomes strictly WEAKER (easier for callers), so no caller can
  newly fail it.

### Re-cross-validation (verbatim, this run)
`test-suite/corpus/pycsl-reference/0716.proofs/{rocq,lean}/DirBlitMarker.{v,lean}`, both
recompiled after adding the `k <> s` / `k ≠ s` freshness hypothesis:

```
# Rocq 8.x — coqc DirBlitMarker.v — Print Assumptions (both theorems): Section Variables only
Section Variables: rd nlen nchar name_t disk      (0 Axiom / 0 Admitted)

# Lean 4.31.0 — lean DirBlitMarker.lean — #print axioms:
'UnixFs.Dir.dir_blit_marker_intro'  does not depend on any axioms
'UnixFs.Dir.dir_blit_marker_insert' depends on axioms: [propext, Quot.sound]   (⊆ allowlist)
```

## 3. GENUINENESS EVIDENCE — all FOUR bar items (PYTHONHASHSEED=0, best-of-N Alt-Ergo+Z3)

On `--fun unixinodefilesystem___write_dir_entry`:

| # | bar item | probe | result |
|---|----------|-------|--------|
| 1 | **Consistency** | `#@ ensures/assert (inode_num != 0 and inode_num < 32) ==> 1 == 0` | **Unknown** (Timeout 30s / 187K steps) — live branch NO LONGER inconsistent. Dead-branch counter-probe stays Unknown. |
| 2 | **Genuine value** | real `slot_inode==inode_num` + `slot_name==name` (+frames) | **Valid** (whole `--fun` SUCCESS; the two slot decodes ~4274 steps) |
| 3 | **Non-vacuity / falsification** | wrong value `slot_inode(...)==inode_num + 1` | **Unknown / RED** (Postcondition unproven) — proves (2) is real |
| 4 | **Frames** | the two `∀k≠slot` frame postconditions | **Valid** (in the SUCCESS of (2)); wrong-slot frame `∀k≠slot. slot_name==name` → **RED** (1 unproven) |

**Soundness probe (non-canonical populated disk):** with
`#@ requires slot != 3 and slot_inode(self.dir, 5, 3) == 3` added:
- consistency `1==0` probe → **Unknown** (still consistent — NOT an empty-disk artifact)
- genuine value+frame ensures → **Valid** (`--fun` SUCCESS)

(Note on the `\old`-based wrong-slot frame falsification: a falsification stated via
`\old(slot_inode(...))` at k=slot spuriously PASSES because the same in-place-mutation
`\old==post` aliasing collapses `\old(slot_inode(self.dir,5,slot))` to the post-state value.
That is a *probe-construction* artifact of the array aliasing, NOT a residual vacuity — the
collapse-immune wrong-slot frame falsification in (4) correctly REDs, and the genuine
postconditions [discharged via the marker's `d1`] are unaffected.)

## 4. SCOPE / WHAT IS AND IS NOT CLOSED
- **Closed:** the live-inode-branch VACUITY (the soundness bug). The marker substrate is now
  SOUND at `--fun` level: genuine, falsification-confirmed, soundness-probe-clean, zero-TCB
  cross-validated.
- **NOT in scope (unchanged from v2):** the FULL-body-gate retirement still faces the
  catalog-B A.7 aggregate-context E-matching wall (a step-budget/packaging problem, not
  vacuity). Making the now-SOUND substrate also discharge the full gate needs the scope-feature
  or prover/trigger tuning — a separate, human-gated follow-on. This repair makes that pursuit
  viable (the substrate is no longer vacuous).

## 5. DELIVERABLES
- `getting-better/PROPOSAL-write-dir-entry-detrust-v3-vacuity-repaired.patch` — self-contained
  (superset of v2): the marker registry + predicate + de-trust + direct-write `_blit_dir_entry`
  + `_pad_name` ensures + **the v3 freshness `k≠s` repair** + the re-cross-validated proof
  sources. `git apply` from repo root, applies clean on HEAD (verified).
- Re-cross-validated sources inside the patch:
  `test-suite/corpus/pycsl-reference/0716.proofs/{rocq,lean}/DirBlitMarker.{v,lean}`.

## 6. TREE STATE
NOT committed. Working tree = clean HEAD + v2-substrate + the v3 repair (the two source files
and the two proof sources), plus this writeup and the v3 patch under `getting-better/`. Stash
empty; compiled Rocq artifacts (.vo/.glob/.aux/.lia.cache) cleaned from the proofs dir. The
parent re-runs all four genuineness probes from the v3 patch before trusting the repair.
