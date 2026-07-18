# Impl plan: break the list-append-mutation wall → the 22-marker C bucket

**Inputs:** `20260718-0633-stmt-list-append-mutation-wall.md` (U) ∧ `-response.md` (fable: **BREAKABLE**,
sound model hand-proven Valid, 0 axioms). **Discipline:** spike-first, refutation-exit. Do NOT launch the
family build until the make-or-break SPIKE passes ALL its gates.

## The sound model (fable-proven — `/tmp/wall-oracle/sound_append.mlw`, both VCs Valid, 0 axioms/0 abstract vals)
- A statement-IR param becomes a caller-visible mutable region: `ir_stmts : ref (seq stmt_ir)` with a real
  `writes { ir_stmts }` frame. `.append(v)` → `ir_stmts := Seq.snoc !ir_stmts v` on the **parameter's ref**
  (NOT a local snapshot copy). Caller reads `!ir_stmts` after the call and observes the appended element.
- `type stmt_ir = SPass | SBreak | SContinue | SReturn emit_ir | SExpr emit_ir | ...` — monomorphic, sibling
  of the certified `emit_ir` ADT; references `emit_ir` for expr children (NOT mutually recursive → emit_ir
  does not use stmt_ir). Preserves the node tag (no erasure to `0`). Gate the whole block on
  `_uses_stmt_ir()` (Constant-field precedent from `pyconst_val`, commit 2b2927bc) so only the M5 mirror
  emits it → other mirrors + corpus byte-identical.
- The convention is keyed on the syntactic shape the 22 handlers share: **returns `None` + `#@ assigns <the
  list param>`**. Programs that build-and-RETURN a list keep the existing immutable-seq snapshot path
  untouched (its corpus byte-diff stays 0). The two conventions coexist, discriminated by that shape.

## STEP 0 — make-or-break SPIKE (Gate S). ONE handler. If any sub-gate fails, the BREAKABLE verdict is refuted; STOP + re-report to fable.
Target: `_py_stmt_pass` (simplest: appends a nullary node) AND `_py_stmt_return` (appends a node holding one
emit_ir child — tests the expr-child path). Port verbatim; drop `\trusted`; `#@ assigns ir_stmts`.
Gates, ALL required:
1. `--fun` DISCHARGES with a **real `writes { ir_stmts }`** in the emitted `.mlw` (grep it — NOT `writes { }`).
2. **Tag-preserving:** `_py_stmt_pass` and `_py_stmt_break` (or `_py_stmt_return`) emit **DISTINCT** WhyML
   (real `SPass` vs `SBreak`/`SReturn` ctor, NOT both `0`). Emit-and-diff the two bodies.
3. **OBSERVATIONAL non-vacuity (the load-bearing gate — `--check-vacuity` MISSED this, per fable):** author a
   reference-corpus DRIVER that calls the handler on a fresh `ir_stmts`, then reads it back and asserts the
   appended node has the RIGHT tag. Add its evil twin: a driver asserting the WRONG tag that MUST stay
   UNPROVEN. If the wrong-tag twin proves, the frame/model is vacuous → refuted.
4. No new axiom (allowlist unchanged; `Print Assumptions` on any certificate closed). Corpus byte-diff 0
   (the `_uses_stmt_ir` gate makes non-M5 files inert). Whole-file M5 proof SUCCESS. Suite 35/35 (decompose
   if the monolith is killed under load: confirm only M5's `.mlw` changed + M5 proves standalone).

## STEP 1 — co-land the axiom-free certificate (coupling rule, lesson 5)
`src/formal-semantics/rocq/Phase2d_StmtIR.v` + `lean/PyCSL/StmtIR.lean` (the `Phase2c_PyConstVal` precedent):
stmt_ir is a well-founded inductive with a size measure + decidable eq; the dict→ctor map
(`{"stmt":"Pass"}↦SPass`, …) is total+injective on the recognized key-set; the emit_ir child introduces no
mutual recursion. **Also certify the mutable-ref append convention is sound** (append then read observes the
element) OR cite that it is a Why3-intrinsic `writes` VC needing no certificate (decide + record which).
Verify ledger stays 3 (`Print Assumptions` / `#print axioms`).

## STEP 2 — family build, in dependency order, ONE stub per gate battery (only after Gate S passes)
Nullary/simple first: `_py_stmt_pass`, `_py_stmt_break`, `_py_stmt_continue`, `_py_stmt_return`,
`_py_stmt_expr`, `_py_stmt_assert`, `_py_stmt_raise`, `_py_stmt_delete`, `_emit_ghost_assign`. Then the
sub-body-list handlers (need nested `ir_stmts` recursion): `_py_stmt_if`, `_py_stmt_while`, `_py_stmt_for`,
`_process_if`, `_process_while`, `_process_for`, `_py_stmt_with`, `_py_stmt_try`. Then the dispatcher
`_py_stmts_to_ir`. Assess separately (may need extra sub-infra, SKIP if not whole-body-clean):
`_py_stmt_assign`/`_augassign`/`_annassign` (targets + value), `_py_stmt_match` (match-pattern ADT).
Each stub: whole-body port, observational non-vacuity twin, byte-diff additive, count strictly drops.

## Est. yield & cost
Up to ~22 markers (1075 → ~1053) if the sub-body-list + assign/match handlers all fall out; realistic first
pass ≈ the 9 simple + several sub-body handlers. Cost: STEP 0 spike ≈ a pyconst_val-scale build (theory
emission + convention recognizer + retype + certificate) — budget a multi-hour session; do STEP 0 to
completion (commit or refute) BEFORE STEP 2. Return to the cheap-drain loop after: a broken wall may not
unlock new cheap stubs here (census E/F are separate walls), so proceed straight into STEP 2.
