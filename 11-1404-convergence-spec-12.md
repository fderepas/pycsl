STATUS: IMPLEMENTED-PARTIAL

<!-- IMPLEMENTATION OUTCOME (gap-12 turn):
WALL A LIFTED + lemma REGISTERED + dual-kernel validated + proofs shipped +
byte-diff IDENTICAL — but the CLASS-INVARIANT ACTIVATION walls on TWO discharge
gaps, so the trusted `_dir_find_slot` uniqueness ensures is NOT yet removed.
PER-RESIDUAL-HANDLING: did NOT re-trust, did NOT fake; kept os GREEN at the last
working stage (invariant inactive) + wrote the follow-on gap doc.

WHAT LANDED:
- Wall A fix in src/pycsl/Module6_WhyMLTranspiler.py (transpile(): call
  `_precompute_axiom_logic_funcs` before `_emit_type_decls`; gated
  `_emit_uncited_axiom_func_decls` before type decls via the NEW
  `_class_inv_refs_axiom_func(ir)` predicate in module6_whyml/preamble.py).
  GATE VERIFIED: full-corpus byte-diff (bin/byte-diff-sweep.sh before-vs-after,
  595 files) = 0 differences. os's existing class invariants stay byte-identical.
- `UnixFs.Dir.insert_preserves_unique` registered in _AXIOM_REGISTRY
  (preamble.py). Both kernels ACCEPT the shipped proofs
  (unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/InsertPreservesUnique.{v,lean}):
  Rocq exit 0 / Print Assumptions Closed; Lean exit 0 / axioms = [propext, Quot.sound].
- axiom-registry.md UnixFs.Dir.* 3 -> 4.
- When the invariant was ACTIVATED, the 7 directory mutators' insert-side
  maintenance PROVED under the cited lemma. 3 goals walled (NOT the directory
  maintenance): VC1 constructor establishment Unknown, VC2 `_filesystem` global
  establishment Unknown (both need an empty-disk-decode axiom — `slot_inode` of a
  zeroed disk is uninterpreted, so vacuity is not derivable), VC3 chmod type-
  invariant Timeout (a class invariant obligates EVERY `assigns self.disk`
  method, incl. non-directory writers, which balloon).

PER-MUTATOR TALLY (with invariant active):
  sys_mkdir / sys_link / sys_rename / sys_symlink / sys_creat — insert-side
    maintenance PROVED (cited insert_preserves_unique).
  sys_unlink / sys_rmdir / rename-old-zero — remover maintenance PROVED directly.
  ESTABLISHMENT (constructor + _filesystem) — WALLED (Wall E: empty-disk axiom).
  NON-DIRECTORY `assigns self.disk` writers (chmod, ...) — WALLED (Wall M:
    block-5-decode frame missing).

Residual scoped in 11-1404-convergence-gap-13.md (Wall E + Wall M + fixes).
Last working stage: invariant INACTIVE, `_dir_find_slot` uniqueness ensures
RETAINED + clearly marked, os GREEN. -->


<!-- COORDINATION APPROVAL (editorial):
- LEMMA APPROVED: `UnixFs.Dir.insert_preserves_unique` — both kernels accept (Rocq Closed, Lean ⊆
  {propext, Quot.sound}), finite case split (no induction), faithful (asserts only the structural
  no-dup-created fact under EEXIST + the _write_entry frame; says nothing about decode-vs-bytes). Same trust
  KIND as the accepted `remove_reflects_absent`. The remover side needs NO axiom. This MOVES uniqueness OUT
  of the trusted ensures and into a dual-kernel-anchored axiom + SMT-discharged maintenance — the user's goal.
- WALL A FIX APPROVED: (1) call `_precompute_axiom_logic_funcs` before `_emit_type_decls`; (2) emit the
  axiom-func `val function` decls before the record, GATED by a new `_class_inv_refs_axiom_func(ir)`
  predicate (mirroring the gap-9 conditional reorder). MANDATORY: the reorder MUST stay behind the gate —
  os's 13 existing class invariants reference only \length/disk[i]/scalars (verified), so the gate is False
  for the whole corpus and the byte-diff stays IDENTICAL; an UNCONDITIONAL reorder would shift os's
  val-function lines and break byte-diff. The full-corpus sweep is the catch.
- INTEGRATION: register axiom → activate the uniqueness class invariant (vacuous at _format_disk) → adders
  cite insert_preserves_unique (EEXIST + frame supply the hypotheses), removers preserve directly → DROP the
  `\trusted` uniqueness ensures at `_dir_find_slot` (it now follows from the invariant).
- RESIDUAL (accepted): the 16-slot maintenance VC sits on the E-matching surface that forced `no_inline`;
  trigger-tuning (`assert`/`by`/`no_inline` at the mutator) is fine — but do NOT re-trust uniqueness. If it
  genuinely walls after tuning, keep os GREEN at the last stage + document; do NOT fake.
Acceptance bar: both kernels accept the lemma; full-corpus byte-diff IDENTICAL (os class invariants
byte-identical); os re-proves GREEN; the 7/7 formal_os_namespace consequences STILL VALID; the `\trusted`
uniqueness ensures on `_dir_find_slot` is REMOVED (uniqueness now PROVEN). Set STATUS: DONE on success, else
IMPLEMENTED-PARTIAL with the honest state. -->

<!-- (orig spec-phase header) DRAFT output for gap-12: validated insert_preserves_unique on both kernels,
scoped the Wall A src/pycsl fix (file:line), integration path, gate, RISKS. -->


# Spec-12 — PROVEN directory-uniqueness class invariant (validate lemma + scope Wall A)

STATUS: DRAFT

## 0. Verdict

- **Lemma `UnixFs.Dir.insert_preserves_unique`: GOES THROUGH BOTH KERNELS.**
  Rocq 8.20.1 ACCEPT, `Print Assumptions` = Closed (only Section Variables /
  parameters, no `Axiom`/`Admitted`). Lean 4.30.0 ACCEPT, `#print axioms` =
  `[propext, Quot.sound]` ⊆ allowlist, no `sorry`. Exactly the finite 4-way case
  split gap-12 predicted; no induction. The companion remover side needs NO axiom
  (clearing a slot only shrinks the live set — provable directly in WhyML).
- **Wall A is LOCALIZABLE + BYTE-ADDITIVE.** Two one-shot changes in
  `src/pycsl/Module6_WhyMLTranspiler.py` / `preamble.py`, both gated so they fire
  ONLY when a class invariant references an axiom-backing logic function. No
  existing corpus class invariant does (os's 12 invariants reference only
  `\length`, `self.disk[i]`, and field comparisons — verified below), so the
  full-corpus byte-diff stays IDENTICAL.

## 1. The validated lemma (paste + kernel evidence)

### 1.1 WhyML statement to register (gap-12 §3.1, transcribed faithful)

```
"UnixFs.Dir.insert_preserves_unique":
  "forall d0 : array int. forall d1 : array int. forall blk : int.
   forall s : int. forall nm : string.
   ( forall j : int. 0 <= j < 16 -> slot_inode d0 blk j >= 0 ) ->
   ( 0 <= s < 16 ) ->
   ( forall i j : int. 0 <= i < 16 -> 0 <= j < 16 ->
        slot_inode d0 blk i <> 0 -> slot_inode d0 blk i < 32 ->
        slot_inode d0 blk j <> 0 -> slot_inode d0 blk j < 32 ->
        slot_name d0 blk i = slot_name d0 blk j -> i = j ) ->
   ( forall k : int. 0 <= k < 16 ->
        slot_inode d0 blk k <> 0 -> slot_inode d0 blk k < 32 ->
        slot_name d0 blk k <> nm ) ->
   ( forall k : int. 0 <= k < 16 -> k <> s ->
        slot_inode d1 blk k = slot_inode d0 blk k /\
        slot_name  d1 blk k = slot_name  d0 blk k ) ->
   ( slot_inode d1 blk s <> 0 -> slot_inode d1 blk s < 32 ) ->
   ( slot_name  d1 blk s = nm ) ->
   ( forall i j : int. 0 <= i < 16 -> 0 <= j < 16 ->
        slot_inode d1 blk i <> 0 -> slot_inode d1 blk i < 32 ->
        slot_inode d1 blk j <> 0 -> slot_inode d1 blk j < 32 ->
        slot_name d1 blk i = slot_name d1 blk j -> i = j )"
```

Reuses the already-registered `slot_inode`/`slot_name` symbols
(`_AXIOM_FUNCTIONS["UnixFs.Dir."]`, `preamble.py:235-236`); NO new
`_AXIOM_FUNCTIONS` entry. It is the INSERT companion of the already-registered
`remove_reflects_absent`.

### 1.2 Rocq proof (ran ACCEPT, `Print Assumptions` Closed) — `/tmp/InsertPreservesUnique.v`

```coq
Require Import Coq.ZArith.ZArith.
Require Import Lia.
Open Scope Z_scope.
Module UnixFs. Module Dir. Section Scan.
Variable disk : Type. Variable name_t : Type.
Variable slot_inode : disk -> Z -> Z -> Z.
Variable slot_name  : disk -> Z -> Z -> name_t.

Theorem insert_preserves_unique :
  forall (d0 d1 : disk) (blk s : Z) (nm : name_t),
    (forall j, 0 <= slot_inode d0 blk j) ->
    0 <= s < 16 ->
    (forall i j, 0 <= i < 16 -> 0 <= j < 16 ->
        slot_inode d0 blk i <> 0 -> slot_inode d0 blk i < 32 ->
        slot_inode d0 blk j <> 0 -> slot_inode d0 blk j < 32 ->
        slot_name d0 blk i = slot_name d0 blk j -> i = j) ->
    (forall k, 0 <= k < 16 ->
        slot_inode d0 blk k <> 0 -> slot_inode d0 blk k < 32 ->
        slot_name d0 blk k <> nm) ->
    (forall k, 0 <= k < 16 -> k <> s ->
        slot_inode d1 blk k = slot_inode d0 blk k /\
        slot_name  d1 blk k = slot_name  d0 blk k) ->
    slot_name d1 blk s = nm ->
    (forall i j, 0 <= i < 16 -> 0 <= j < 16 ->
        slot_inode d1 blk i <> 0 -> slot_inode d1 blk i < 32 ->
        slot_inode d1 blk j <> 0 -> slot_inode d1 blk j < 32 ->
        slot_name d1 blk i = slot_name d1 blk j -> i = j).
Proof.
  intros d0 d1 blk s nm Hnn Hs Hinv0 Hfresh Hframe Hsnm i j Hi Hj Hil Hib Hjl Hjb Hnameq.
  destruct (Z.eq_dec i s) as [Eis|Nis]; destruct (Z.eq_dec j s) as [Ejs|Njs].
  - lia.
  - exfalso. subst i.
    destruct (Hframe j Hj Njs) as [Hij Hnj].
    apply (Hfresh j Hj).
    + rewrite <- Hij. exact Hjl.
    + rewrite <- Hij. exact Hjb.
    + rewrite <- Hnj. rewrite <- Hnameq. exact Hsnm.
  - exfalso. subst j.
    destruct (Hframe i Hi Nis) as [Hii Hni].
    apply (Hfresh i Hi).
    + rewrite <- Hii. exact Hil.
    + rewrite <- Hii. exact Hib.
    + rewrite <- Hni. rewrite Hnameq. exact Hsnm.
  - destruct (Hframe i Hi Nis) as [Hii Hni].
    destruct (Hframe j Hj Njs) as [Hij Hnj].
    apply (Hinv0 i j Hi Hj).
    + rewrite <- Hii. exact Hil.
    + rewrite <- Hii. exact Hib.
    + rewrite <- Hij. exact Hjl.
    + rewrite <- Hij. exact Hjb.
    + rewrite <- Hni, <- Hnj. exact Hnameq.
Qed.
Print Assumptions insert_preserves_unique.
End Scan. End Dir. End UnixFs.
```

`coqc InsertPreservesUnique.v` exit 0. `Print Assumptions` prints only the four
Section Variables (`disk`, `name_t`, `slot_inode`, `slot_name`) as parameters —
NO `Axiom`, NO `Admitted` → Closed under the global context.

(Minor deviation from gap-12 §3.2 sketch: the cross-cases discharge the `Hfresh`
premises with explicit `rewrite <- Hij` / `rewrite <- Hii` on the inode bounds —
the sketch's `rewrite ...; try assumption` worked, but the explicit form makes
the goal order unambiguous. Same proof, same shape.)

### 1.3 Lean proof (ran ACCEPT, axioms ⊆ allowlist) — `/tmp/InsertPreservesUnique.lean`

Mirrors the statement in `namespace UnixFs.Dir` `section Scan` with
`variable (slot_inode …) (slot_name …)`. Case split via `Decidable.em (i = s)` /
`Decidable.em (j = s)` (core Lean — NO Mathlib needed, so no `eq_or_ne`), cross
cases closed by `Hfresh` on the framed slot, off-diagonal by `Hinv0`, integers by
`omega`. `lean InsertPreservesUnique.lean` exit 0:

```
'UnixFs.Dir.insert_preserves_unique' depends on axioms: [propext, Quot.sound]
```

⊆ {propext, Quot.sound}, no `sorry`. PASS.

## 2. Wall A — the src/pycsl TOOL fix (file:line)

### 2.1 Root cause (confirmed)

The class-invariant lowering loop is `preamble.py:1328-1332`:
```
inv_str = self._expr_to_whyml(inv, set(), invariant_ctx=True)
```
This is inside `_emit_class_records` (the loop in `_emit_type_decls`,
`preamble.py:1152+`). A call `slot_inode(self.disk, 5, k)` reaches the call
lowering in `expressions.py:1120`:
```
if func_name in getattr(self, "_axiom_logic_funcs", set()):
    return f"({func_name} {' '.join(args)})" ...
```
That recognition is context-INDEPENDENT — it would resolve `slot_inode` raw IF
the name were in `self._axiom_logic_funcs`. **It is not, at invariant-emit time.**

Orchestration order in `Module6_WhyMLTranspiler.py`:
- L390 `_emit_type_decls(...)` ← class records + invariants lowered HERE.
- L407 `self._precompute_axiom_logic_funcs(self.ir)` ← `_axiom_logic_funcs` first
  populated HERE (and again inside `_emit_preamble_axioms`, `preamble.py:801`).

So at L390 `getattr(self, "_axiom_logic_funcs", set())` returns the EMPTY default
(attribute unset). `slot_inode` is treated as an unknown applied symbol and falls
to the unannotated-callee arm `expressions.py:1145-1182`:
```
safe_fn = whyml_ident(func_name)        # slot_inode
arity_fn = f"{safe_fn}_{n}"             # n = 3  →  slot_inode_3   <-- the mangle
self._add_abstract_op("val slot_inode_3 (x0: int) (x1: int) (x2: int) : int")
```
→ `unbound function or predicate symbol 'slot_inode_3'` (gap-12 §2). **Sub-problem
1 = the precompute runs AFTER the invariant is lowered.**

Sub-problem 2 (ordering): the real `val function slot_inode/slot_name/dir_lookup`
decls are emitted by `_emit_preamble_axioms` (`preamble.py:798`) and
`_emit_uncited_axiom_func_decls` (`preamble.py:1019+`), appended at
`Module6_WhyMLTranspiler.py:416-426` — AFTER L390's type decls. Even with the
symbol resolved, the record `invariant { ... slot_inode ... }` references symbols
declared LATER in the file → still unbound.

### 2.2 The fix (two gated, byte-additive moves)

**Fix part 1 — symbol resolution (precompute earlier).** Move/duplicate the
`_precompute_axiom_logic_funcs(self.ir)` call to BEFORE `_emit_type_decls`
(`Module6_WhyMLTranspiler.py:390`). It is documented idempotent
(`preamble.py:702-703`) and already called again at L407 and inside
`_emit_preamble_axioms` — so an extra early call changes nothing for any file
that doesn't apply an axiom func in an invariant. This is the EXACT analogue of
the gap-9/gap-10 contract-context fix: resolve `_AXIOM_FUNCTIONS` symbols raw via
`_axiom_logic_funcs` rather than uniquifying with a `_<n>` suffix.

**Fix part 2 — declaration ordering (emit axiom-func decls before the record
that needs them).** When a class invariant references an axiom function, emit the
matching `val function` decls (the registry decls for the cited/used
`_AXIOM_FUNCTIONS` symbols, via the existing `_emit_uncited_axiom_func_decls` /
the `_emit_preamble_axioms` decl block) BEFORE the `_emit_type_decls` output is
appended — cf. the abstract_ops.py insert-point advancement and the gap-9
conditional reorder (`Module6_WhyMLTranspiler.py:415-419`). Concretely: factor
the axiom-func `val function` decl emission so it can run before L390, GATED by a
new predicate analogous to `_inductive_refs_global_or_axiom_func`
(`preamble.py:649-689`) — call it `_class_inv_refs_axiom_func(ir)` — that returns
True iff some `class_invariants` IR node is a `Call` to a name in
`_axiom_logic_funcs`. When False (every existing file), nothing reorders → output
byte-identical.

### 2.3 Byte-additivity evidence

os's existing class invariants (`pure_lib/os/UnixInodeFileSystem.py:435-445` +
`pure_lib/os/__init__.py:59`) reference ONLY `\length(self.disk)`,
`self.disk[i]`, `self._inode_num`, and the `fd_*`/`next_fd`/`cur_*`/`_mtime_ticks`
fields — NONE applies `slot_inode`/`slot_name`/`dir_lookup`. So
`_class_inv_refs_axiom_func` returns False for the entire current corpus → both
fix parts are no-ops on every existing emission → full-corpus byte-diff IDENTICAL.
The path activates only for the NEW uniqueness invariant the stdlib-agent adds.

## 3. Integration path (after Wall A fixed + lemma registered)

1. Tool-agent (post-APPROVAL) applies the Wall A fix (§2.2) and registers
   `UnixFs.Dir.insert_preserves_unique` (§1.1) in `_AXIOM_REGISTRY`
   (`preamble.py:18+`) behind the dual-kernel gate (§1.2/§1.3 evidence).
2. STDLIB-AGENT uncomments the uniqueness `#@ class invariant`
   (`UnixInodeFileSystem.py:454-457`, the §2-Wall-A block) over the
   `UnixInodeFileSystem` record. `_format_disk` establishes it VACUOUSLY (slots
   0,1 dead → no live pair).
3. Each ADDER (`sys_mkdir`, `sys_link` newpath, `sys_open` O_CREAT,
   `sys_symlink`, `sys_creat`) MAINTAINS it citing `insert_preserves_unique`: the
   EEXIST guard already on each adder supplies the "nm not already live"
   hypothesis; `_write_entry`'s slot-locality frame ensures supplies the "d1
   agrees with d0 off s" frame; the write supplies "slot s live with name nm".
4. Each REMOVER (`rmdir`, `unlink`) MAINTAINS it DIRECTLY (no axiom): clearing a
   slot via `_zero_entry` only shrinks the live set; discharged from the
   slot-locality frame + the invariant on `\old`.
5. DROP the 3rd `#@ ensures` (the trusted uniqueness clause) on `_dir_find_slot`
   (`UnixInodeFileSystem.py:795`). Its callers (the removers) read uniqueness off
   the now-proven class invariant at the removal site. Uniqueness LEAVES the TCB.
   (The first two `\result`↔disk-decode ensures may stay `\trusted dirscan-fidelity`
   per gap-12 §0 — only UNIQUENESS becomes proven.)
6. Re-gate: os GREEN, 7/7 `formal_os_namespace.py` VALID, byte-diff identical,
   conformance 38/38, doc-coherency green. Add `glossary/axiom-registry.md` +
   `docs/pycsl-helper-tools.md` entries for the new axiom.

**Residual SMT honesty:** activating the invariant adds a maintenance VC per
mutator that is quantified over the 16 slots against the same E-matching surface
that forced `#@ no_inline` + entry-write-last to keep os GREEN (gap-9 §3c). The
lemma collapses the hard "no new duplicate pair" obligation to a single cited
application, but Alt-Ergo/Z3 may still need the adders' EEXIST-guard fact and the
`_write_entry` frame instantiated at the right slot. Expect possible
trigger-tuning (explicit `assert`/`by` at the mutator, or pinning the frame
instantiation) — NOT a re-trust. This is the stdlib-agent's follow-on cost.

## 4. Gate

- [x] Both kernels ACCEPT `insert_preserves_unique` (Rocq Closed; Lean ⊆
      {propext, Quot.sound}). — DONE this turn (§1.2/§1.3).
- [ ] Wall A fix byte-additive: full-corpus byte-diff IDENTICAL (os's existing
      class invariants stay byte-identical). — verify on implementation turn.
- [ ] After stdlib follow-on: os re-proves GREEN; 7/7 `formal_os_namespace.py`
      consequences STILL VALID; `\trusted` uniqueness ensures REMOVED from
      `_dir_find_slot`.
- [ ] doc-coherency green; conformance 38/38; new axiom documented in
      glossary/axiom-registry.md + docs/pycsl-helper-tools.md.

## 5. RISKS (for the user's judgment)

**(a) Does the lemma go through both kernels? — YES, cleared this turn.** Rocq
8.20.1 `coqc` exit 0, `Print Assumptions` Closed (no Axiom/Admitted; only the
abstract Section Variables). Lean 4.30.0 exit 0, `#print axioms` =
`[propext, Quot.sound]`, no `sorry`. Finite 4-way case split, no induction —
exactly as gap-12 predicted. This was the make-or-break; it is GREEN.

**(b) Is Wall A truly localizable + byte-additive? — YES, with one caveat to
verify on implementation.** Both fix parts are GATED on
`_class_inv_refs_axiom_func(ir)` (an invariant applies an axiom func), which is
False for the ENTIRE current corpus (os's 12+1 class invariants reference only
`\length`/`self.disk[i]`/fields — confirmed, none calls
`slot_inode`/`slot_name`/`dir_lookup`). The early `_precompute_axiom_logic_funcs`
is idempotent and already runs twice more, so it cannot perturb a file that
doesn't trigger. CAVEAT: the implementor must keep the decl-ordering move BEHIND
the gate (mirroring the gap-9 conditional reorder at L415) — an UNCONDITIONAL
reorder of the axiom-func decls before type decls WOULD shift os's
`val function slot_inode/...` lines earlier and break byte-diff. The full-corpus
byte-diff sweep is the gate that catches a mis-gate.

**(c) TCB — what does `insert_preserves_unique` assert (faithful)?** It asserts
ONLY the structural fact: starting from a disk whose 16 live slots have no
duplicate live names, if you make ONE slot `s` live with a name `nm` that was NOT
already among the live names (the EEXIST precondition), and EVERY other slot is
byte-for-byte unchanged (the `_write_entry` slot-locality frame), then the
resulting disk still has no duplicate live names. It is NOT over-strong: it does
not assert anything about the decode function's relationship to raw bytes (that
stays in the trusted `dirscan-fidelity` decode ensures), only that a fresh-name
single-slot insert under an unchanged frame cannot manufacture a duplicate pair.
The remover direction needs no axiom (clearing a slot shrinks the live set,
WhyML-direct). Net TCB change: uniqueness MOVES OUT of the trusted ensures and
becomes a dual-kernel-anchored axiom of the same kind as the already-accepted
`remove_reflects_absent` — and the per-mutator MAINTENANCE is SMT-discharged, not
trusted.

## 6. State at end of this turn

- spec-12 at STATUS: DRAFT.
- NO src/pycsl edits, NO axiom registered, NO git ops.
- Lemma validated on BOTH kernels (probes in `/tmp/InsertPreservesUnique.v` and
  `/tmp/InsertPreservesUnique.lean`).
- Wall A root-caused to `Module6_WhyMLTranspiler.py:390` (type decls) vs L407
  (precompute) ordering + `expressions.py:1120/1145-1182`
  (`slot_inode`→`slot_inode_3` mangle) + decl emission at L416-426 after L390.
- Fix specified, gated, byte-additive; implementation deferred to APPROVAL.
