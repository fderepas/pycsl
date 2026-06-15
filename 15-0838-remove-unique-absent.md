# Spec: closing the directory-absence proof via SCOPED elims + a delivered `remove_unique_absent`

**Status:** specification (2026-06-15). The real fix for M4 (close `sys_unlink`/`sys_rmdir`/
`sys_rename`'s post-removal absence). Supersedes the three failed M4 attempts documented in
`14-1814-os-roadmap.md` (Layer-2 frame / `uniq_absent` / `remove_unique_absent` as an always-emitted
axiom). **The fix is a Module6 EMISSION change (scoped/cited elims), NOT a new axiom.**

---

## 1. The problem

The directory removers must, after zeroing the target slot `s`, discharge the ABSENCE witness that
`remove_reflects_absent` consumes:

```
\forall k. 0<=k<16 -> k<>s -> slot_name(self.disk,5,k) == pathname -> slot_inode(self.disk,5,k) == 0
```

`sys_rmdir` proves it (lean body); `sys_unlink`/`sys_rename` do NOT — they **time out / OOM**
(6.8M–13.7M steps). Three attempts to supply the missing fact (the Layer-2 quantified frame,
`uniq_absent`, `remove_unique_absent` as a registry axiom) all failed for the SAME reason.

## 2. Root cause — a STRUCTURAL Why3 limitation, not a missing lemma

The absence is a first-order consequence of the directory uniqueness invariant: in a `uniq` +
`slots_lt32` disk where `s` is the unique live `pathname` entry, every other same-named slot is
dead. The lemma exists and is correct (`remove_unique_absent`, a zero-TCB consequence of
`uniq_elim`+`slots_lt32_elim`+the zero frame). **But supplying it does not help**, because:

- `uniq_elim` / `slots_lt32_elim` are emitted in **`_CLASS_INV_AXIOMS`** (always, before the record),
  so they are in scope for **every** VC in the os module, triggered on the ubiquitous `uniq self.disk`
  / `slots_lt32 self.disk` class-invariant atoms.
- In a TERM-RICH body (`sys_unlink`'s inode-block-freeing loop accumulates many `slot_inode`/
  `slot_name` terms across several disk versions), `uniq_elim`'s `\forall i j` and `slots_lt32_elim`'s
  `\forall k` instantiate combinatorially → **E-matching explosion**, regardless of any O(1) lemma
  also in scope. (`sys_rmdir` escapes only because its body is lean — no loop.)
- These elims **cannot be removed** (the loop + the per-method type-invariant maintenance need them
  to fold/unfold `uniq`), and **cannot be scoped per-goal** — Why3 axioms are module-global, in scope
  for all sub-goals of all functions.
- Worse, any **new always-emitted** quantified directory axiom adds its own noise: `uniq_absent`
  regressed `sys_rename` 2→3, `remove_unique_absent` regressed it 2→3 again.

So: the absence proof needs the uniqueness FACT but is poisoned by the uniqueness ELIM that must stay
in scope. **The fix is to remove the elims from the syscalls' VC context while keeping them where
maintenance needs them — a per-function emission change — and deliver the absence as one applied
fact.**

## 3. The fix (overview)

Two coordinated parts, both EMISSION-level (no new modeling, no new trusted fact):

- **Part A — SCOPE the elims.** Move `uniq_elim` / `slots_lt32_elim` (and the matching `*_intro`)
  out of `_CLASS_INV_AXIOMS` (always-emitted) into **cited-only** emission. They are then emitted
  ONLY in functions that cite them — the LEAF disk-writers, where maintenance needs them and the
  body is lean. The absence-proving syscalls do NOT cite them, so they are absent from those VCs and
  cannot explode.
- **Part B — DELIVER `remove_unique_absent` as one applied fact**, cited by the removers, so the
  absence discharges in O(1) in an elim-free context.

The invariant maintenance that the syscalls used to do via the in-scope elims is instead **inherited
from the leaf writers' contracts** (each leaf writer `ensures` `uniq`/`slots_lt32` is maintained).

## 4. Part A — scope the elims (the central change)

### 4.1 Why the syscalls don't actually need the elims
Every `self.disk` mutation in a syscall already routes through a LEAF writer (`_set_bitmap`, `_poke`,
`_write_inode`, `_write_entry`, `_zero_entry`, `_alloc_*`, `_block_roundtrip`, `format_disk`). If each
leaf writer **ensures the disk invariants are maintained** —

```
#@ ensures uniq(self.disk)        # given uniq held on entry
#@ ensures slots_lt32(self.disk)  # given slots_lt32 held on entry
```

— then a syscall's class-invariant maintenance (incl. loop invariants like `sys_unlink`'s
`#@ loop invariant uniq(self.disk)`) follows from the leaf writers' ensures by transitivity, with
NO `uniq_elim`/`slots_lt32_elim` in the syscall's own VC. The leaf writers prove their maintenance
ensures IN THEIR OWN bodies, where `uniq_elim`+`uniq_intro`+`block5_decode_frame` fire in a LEAN
context (a single byte/region write — like `sys_rmdir`, which already proves under the same elims).

### 4.2 The emission change
- **Remove** `UnixFs.Dir.uniq_intro`, `uniq_elim`, `slots_lt32_intro`, `slots_lt32_elim` from
  `_CLASS_INV_AXIOMS` (so they are no longer always-emitted before the record).
- Keep them in `_AXIOM_REGISTRY` + `_DEFINITIONAL_AXIOMS` (still zero-TCB definitional).
- They are emitted by the existing **cited-axiom path** (`_emit_preamble_axioms`, gated on
  `func["proof"]` containing the qualname) — so a function gets an elim in scope **iff** it carries
  `#@ proof <prover> UnixFs.Dir.uniq_elim` (etc.).
- The `intro` axioms (needed for ESTABLISHMENT) must additionally be available to the constructor
  (the `Array.make` witness folds `uniq`/`slots_lt32` via `*_intro`). Cite them in `__init__`.

CAVEAT — ordering: today these axioms are hoisted before the record because a `#@ class invariant`
references the abstract `uniq`/`slots_lt32` PREDICATES. The class invariant needs only the predicate
SYMBOLS (declared in `_AXIOM_FUNCTIONS`), NOT the intro/elim FACTS — so moving the facts to the
cited (post-type) path is sound; verify the predicate symbols are still declared before the record.

### 4.3 Which functions cite which
- Leaf writers (`_set_bitmap`, `_poke`, `_write_inode`, `_write_entry`, `_zero_entry`, `_alloc_*`,
  `format_disk`, …): cite `uniq_elim`+`uniq_intro`+`slots_lt32_elim`+`slots_lt32_intro` (+ the
  `block5_decode_frame` they already cite) and gain the `ensures uniq /\ slots_lt32` maintenance.
- Removers (`sys_unlink`/`sys_rmdir`/`sys_rename`): cite NEITHER elim; cite `remove_unique_absent`
  (Part B). Their maintenance is inherited; their absence is the applied lemma.
- Other syscalls: cite nothing new; they inherit maintenance from the leaf writers.

## 5. Part B — deliver `remove_unique_absent` (one applied fact)

The lemma (from the reverted attempt 3, correct):
```
forall d0 d1 : array int, s : int.
  uniq d0 -> slots_lt32 d0 ->
  0<=s<16 -> slot_inode d0 5 s <> 0 -> slot_inode d1 5 s = 0 ->
  (forall k. 0<=k<16 -> k<>s -> slot_inode d1 5 k = slot_inode d0 5 k) ->
  (forall k. 0<=k<16 -> k<>s -> slot_name  d1 5 k = slot_name  d0 5 k) ->
  (forall k. 0<=k<16 -> k<>s -> slot_name d1 5 k = slot_name d0 5 s -> slot_inode d1 5 k = 0)
```
`d0` = pre-zero disk, `d1` = post-zero (`_zero_entry`'s `\old`-frame relates them). Multi-trigger
`[slot_inode d1 5 s, slot_inode d0 5 s]` (the `block5_decode_frame` precedent), so it fires O(1)
exactly for the removed slot. It is a FO consequence of `uniq_elim`+`slots_lt32_elim` — **but it is
proved/validated ELSEWHERE so the removers never see those elims.** Two delivery variants:

### Variant B1 — opaque cross-validated cited axiom (RECOMMENDED — simplest, robust)
Emit `remove_unique_absent` only via the cited path (NOT `_CLASS_INV_AXIOMS`), cited by the three
removers. Validate it in Rocq+Lean (`unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/
RemoveUniqueAbsent.{v,lean}`): model `uniq`/`slots_lt32`/`slot_inode`/`slot_name` abstractly, assume
the uniqueness + `<32` + frame hypotheses, prove the absence (finite case split, no induction). The
removers APPLY it; the explosive elims are out of their scope (Part A), so no competition. Adds the
axiom to the TCB as a cross-validated fact (sound; it is in truth implied by the definitional elims,
so the cross-validation is a conservative re-proof — matches the `remove_reflects_absent` pattern).

### Variant B2 — separate minimal Why3 theory + applied lemma (ZERO-TCB, more wiring)
Prove `remove_unique_absent` as a Why3 `lemma` (not axiom) inside a SEPARATE minimal theory
containing ONLY abstract `uniq`/`slots_lt32`/`slot_inode`/`slot_name` + the elims + the lemma — no os
syscalls, no loop. There the `\forall i,j` instantiation is bounded (lean context, like `sys_rmdir`),
so Why3 discharges the lemma. The os imports the lemma as an applied fact. KEEPS zero-TCB (Why3
proves it). Subtlety: a Why3 `use` of the theory also imports its elim axioms — to avoid
reintroducing them into the os, expose the lemma through an abstraction/clone that hides the theory's
axioms (or place the theory's elims under names the os does not also trigger). This is the rigorous
option but needs care in the theory boundary.

**Recommendation:** ship **B1** first (unblocks M4 with a small, auditable cross-validated axiom);
optionally migrate to **B2** later to recover zero-TCB. Either way Part A is required — without it the
removers still see the explosive elims.

## 6. Module6 emission changes (concrete)
1. `preamble.py`: remove the four `*_intro`/`*_elim` qualnames from `_CLASS_INV_AXIOMS`; keep them in
   `_AXIOM_REGISTRY` + `_DEFINITIONAL_AXIOMS`. Add `remove_unique_absent` to `_AXIOM_REGISTRY`
   (cited-only; NOT `_CLASS_INV_AXIOMS`); to `_DEFINITIONAL_AXIOMS` (B2) or leave as a cited
   cross-validated entry (B1).
2. Confirm the cited-axiom path (`_emit_preamble_axioms`, gated on `func["proof"]`) emits these after
   the type/predicate declarations and that ordering still typechecks (predicate symbols precede the
   record via `_AXIOM_FUNCTIONS`).
3. No change to the `#@ proof` citation grammar — reuse it.

## 7. os contract changes
- Leaf writers: add `#@ ensures uniq(self.disk)` + `#@ ensures slots_lt32(self.disk)` (maintenance)
  + `#@ proof rocq/lean UnixFs.Dir.{uniq,slots_lt32}_{intro,elim}` citations.
- `__init__`/constructor: cite the `*_intro` axioms for establishment.
- `sys_unlink`/`sys_rename`: re-add the (B) loop-carry of `slot live + named pathname` (so the
  removed slot is live on `d0`) + `#@ proof … UnixFs.Dir.remove_unique_absent`; keep the existing
  absence `#@ assert`, now discharged O(1).
- `sys_rmdir`: cite `remove_unique_absent` too (uniform; it already closes, this keeps it robust).

## 8. Validation & gating (NON-NEGOTIABLE)
- os `__init__` gate stays **GREEN** (re-run after the emission change — the elim re-scoping touches
  every method's invariant maintenance).
- Body gate: `sys_unlink`/`sys_rmdir`/`sys_rename` reach **0 unproven**; confirm NO regression on the
  leaf writers (now carrying maintenance ensures) or other syscalls. Use a short `--timelimit` fast
  pass for the regression delta (the full gate is slow).
- corpus byte-diff = 0 (os/registry-scoped change; expect byte-safe except deliberate fixtures).
- `remove_unique_absent`: B1 → `--reverify-proofs` (Rocq Closed / Lean ⊆{propext,Quot.sound}) +
  `#@ proof` audit; B2 → the separate theory typechecks + the lemma discharges.
- New `#@`-surface? None (reuses `#@ proof`). If any directive is added, run the language audit +
  5 doc surfaces.

## 9. Risks & alternatives
- **Broad refactor:** re-scoping the elims touches every disk-writer's maintenance proof. Mitigate by
  doing it leaf-writer-by-leaf-writer, gating `__init__` after each (the `uniq` invariant itself took
  gaps 12–13 to land — expect similar care).
- **Maintenance gap:** if some syscall mutates `self.disk` NOT via a maintenance-ensuring leaf writer,
  its invariant VC will lose the elim and fail — audit that ALL disk writes route through ensuring
  helpers (they currently do).
- **B2 theory boundary:** importing the minimal theory may re-leak the elims; if the abstraction is
  fiddly, fall back to B1.
- **Alternative considered & rejected:** tightening the elim triggers in place (keeps them
  always-emitted) — rejected: any trigger that fires for maintenance also fires for the absence in
  the same dense body (attempts 1–3 confirmed). Scoping, not trigger-tuning, is the fix.

## 10. Sequencing
1. Part A: re-scope `*_intro`/`*_elim` to cited-only + add maintenance ensures to ONE leaf writer
   (`_set_bitmap`); gate `__init__`. Iterate across leaf writers.
2. Confirm the removers' bodies still maintain `uniq`/`slots_lt32` via the helper ensures (no elim).
3. Part B1: add `remove_unique_absent` (cited, cross-validated) + cite in the removers + re-add the
   (B) loop-carry; verify `sys_unlink`/`sys_rmdir`/`sys_rename` → 0 unproven.
4. Full gating (§8). Merge `m4-layer2-frame` → main once all green.
5. (Optional) Part B2 migration for zero-TCB.
