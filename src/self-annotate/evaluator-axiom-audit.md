# evaluator-axiom-audit.md — the audited D2 trust boundary

**What this is.** The LINK-3 coherence layer (`pycsl-wp-spec.mlw`, modules `PyCSL_WP_Coherence` /
`PyCSL_WP_Compose`) proves that the emitter is coherent with the WP state-transformer **relative to
an axiomatized denotational semantics of the emitted WhyML strings**. Those axioms — the
`eval_whyml_*` evaluator and its per-construct `*_semantics` facts — are the **irreducible audited
trust boundary** (the "D2" boundary of `the-finishable-path.md`; "Ceiling B" of `facing-the-facts.md`).
This document audits that boundary: it enumerates every evaluator axiom, states what WhyML construct
it models, and gives its justification, so the trust is **short, explicit, and human-checkable**.

**Why these are axioms, not lemmas — and why that is correct, not a gap.** `eval_whyml_stmts` is an
in-logic model of *WhyML's own evaluation*. Proving it sound would require formalizing the WhyML
interpreter inside WhyML and proving that formalization adequate — a reflective/metacircular
construction that, by Gödel/Löb, cannot be fully discharged within the system itself. The realistic
and standard posture (CompCert's machine model, seL4's hardware model, every verified-compiler's
bottom layer) is an **audited semantic model**. The discipline is therefore not *eliminate* the
axioms but *minimize and cite* them — which is what this audit enforces.

**Scope.** These axioms are sound **for the fragment the emitter actually emits** — the statement and
expression shapes produced by `module6_whyml/`. They are NOT claimed for all of WhyML. Scoping to the
emitted fragment is what keeps the set finite (~24 axioms) and auditable.

---

## 0. The two abstract evaluators

| symbol | type | models | audit anchor |
|---|---|---|---|
| `eval_whyml_expr` | `string -> state -> value` | evaluation of an emitted WhyML *expression* string | Phase2_State.v `eval_expr` |
| `eval_whyml_stmts` | `string -> state -> state` | evaluation of an emitted WhyML *statement* string (the post-state) | Phase3_SOS.v `exec` (normal outcome) |

The per-construct axioms below pin `eval_whyml_stmts` on each emitted statement shape.

---

## 1. Structural axioms (the glue)

| axiom | statement (informal) | justification |
|---|---|---|
| `eval_empty_semantics` | `eval "" st = st` | the empty program is the identity on state — definitional. |
| `seq_semantics` | `eval (s1 ^ ";\n" ^ s2) st = eval s2 (eval s1 st)` | WhyML `;` sequencing: run `s1`, then `s2` from the resulting state. The single most-used axiom; it is what makes the CPS composition (`emit_stmts`) decompose. Matches Why3's documented `e1; e2` evaluation. |
| `seq_concat_semantics` | `eval (s1 ^ s2) st = eval s2 (eval s1 st)` | the no-separator variant (when the emitter omits `;\n` for an empty continuation); same justification. |

---

## 2. Per-construct axioms (one family per emitted statement shape)

Each family is the audited counterpart of a Module-6 `_handle_*` emission; together with §1 it pins
the whole emitted fragment. Each row cites the WhyML shape emitted and the Phase4_WP.v WP arm it must
agree with (the agreement is the *proved* `*_code_state_coherent` lemma — NOT audited).

| family | emitted shape (Why3) | axioms | WP arm | justification |
|---|---|---|---|---|
| **skip** | `indent ^ "()"` [`^ ";\n" ^ rest`] | `skip_semantics`, `skip_semantics_norest` | SSkip (`Qn st`) | `()` is WhyML unit — the identity; the rest (if any) runs after. |
| **assign** | `x := e` / `let x = ref e in` / `let x = e in` | `assign_ref_update_semantics`, `assign_let_ref_semantics`, `assign_let_semantics` | SAssign (`update st x (eval e)`) | the three binding forms the emitter chooses (ref-update vs first-decl vs array/lambda/dict) all bind `x` to `eval e` then run rest — Why3 `:=` / `let … in`. |
| **augassign** | `x := !x op e` / `x := (op !x e)` | `aug_assign_arith_semantics`, `aug_assign_bitwise_semantics` | SAugAssign | reads `!x`, applies `op` (arith inline / bitwise via abstract op), rebinds `x`. |
| **arrayset** | `arr[i] <- v` [`^ ";\n" ^ rest`] | `array_set_semantics`, `array_set_semantics_norest` | SArraySet | Why3 array element update `a[i] <- v`; index/value are int-valued (the `VInt` hypotheses). |
| **if** | `if c then begin … end [else begin … end]` | `if_else_semantics`, `if_only_semantics` | SIf | Why3 `if`: dispatch on `c <> VInt 0`; the `else`-less form is the identity on the false branch. |
| **while** | `while c do invariant{…} variant{…} body done` | `while_semantics` (+ `eval_while_fixpoint`) | SWhile | the loop's post-state is the fixpoint of its body over the condition. `eval_while_fixpoint` is the abstract loop denotation; see §3. |
| **return** | `e` / `raise (Return e)` / `raise Return_void` | `return_plain_semantics`, `return_raise_semantics`, `return_void_semantics` | SReturn | plain value / early-return-exception (sets `\result`) / void early-return (state unchanged). |
| **continue** | `raise PyCSL_Continue` | `continue_semantics` | SContinue (`Qc st`) | the continue-exception is caught by the enclosing loop; state passes through. |
| **for (init)** | `let idx = ref 0 in <desugared while>` | `for_code_init_semantics` | SFor | the for-loop initializes `idx := 0` then runs the desugared while; **the full WP equivalence of the desugaring is the open `wp_for_desugar` gap** — see §3 and `formal-semantics-completion.md`. |

---

## 3. The two axioms that carry extra weight (and their open follow-ons)

- **`while_semantics` + `eval_while_fixpoint`.** The loop's denotation is abstract (`eval_while_fixpoint`).
  Its *adequacy* — that it equals the real loop semantics — is NOT closed here. However, the WP rule
  for `SWhile` **is proved sound against the SOS** (`Phase5b_Soundness.v` `pycsl_soundness`, whose
  `Print Assumptions` are only `propositional_extensionality` + `functional_extensionality_dep` — i.e.
  no `Admitted`). So the *while semantics itself is sound*; what stays audited is the evaluator's
  `eval_while_fixpoint` denotation of the emitted while-string. The legacy `Phase5a_WhileInv.v`
  `while_inv_preserved` Admitted is a *separate, alternate* formulation NOT in the soundness closure.
- **`for_code_init_semantics`.** `SFor` desugars to a while; `desugar_correct` (SOS-level) **is proved**
  (`Phase3b_Desugar.v`). The WP-level equivalence (`wp_for_desugar`) is **now also PROVED** —
  `Phase5c_WpForDesugar.v`, `wp_for_desugar` / `wp_desugar_iff`, proves `wp s ↔ wp (desugar s)` (both
  directions; the forward `wp_desugar_fwd` was already in `Phase5b_Soundness.v`, this adds the backward
  direction), with `Print Assumptions` = only the two standard extensionality axioms, **0 Admitted**.
  So the SFor WP arm is now a *proved* mirror of its `SSeq∘SWhile` desugaring; the for-loop is no
  longer an open WP-level gap. (`for_code_init_semantics` remains as the *evaluator*-string axiom for
  the emitted for-init, like every other `*_semantics`.)

---

## 3a. The field/slice/expr arms — now PROVED-coherent (atomic eval axioms only)

These four — `field-assign`, `field-aug`, `slice-set`, `expr-stmt` (SCall) — were **promoted this turn**
to the same tier as the 10 control-flow/core arms: each now has an emitter spec + an **atomic
eval-semantics axiom** (`field_assign_semantics`/`field_aug_semantics`/`slice_set_semantics`/
`expr_stmt_semantics`) + a **proved** coherence lemma (`*_code_state_coherent`, all Z3-Valid). So their
trust is no longer a bundled "coherence" axiom — it is just the atomic eval-semantics axiom (audited,
like every `*_semantics`), and the coherence is machine-checked. The construct **effects remain
abstract** (`field_effect`/`field_aug_effect`/`slice_effect`/`expr_effect` are uninterpreted): a
*concrete, faithful* effect — Phase 7 field-state, an array-slice semantics, Phase 8 SCall — is the only
remaining future work, and it does NOT affect the (already proved) coherence. `critical` is proved
**via its body** (the Hoare-instance `critical_havoc P = P` makes the lock transparent — only the atomic
`critical_wrapper` axiom is audited; real concurrency = Phase 7).

The four atomic eval-semantics axioms (audited, joining §1–§2):

| construct | emitter spec | atomic eval axiom (audited) | proved coherence lemma | abstract effect (future-work) |
|---|---|---|---|---|
| field-assign | `handle_field_assign_code` | `field_assign_semantics` | `field_assign_code_state_coherent` ✓ | `field_effect` — Phase-7 field-state |
| field-aug | `handle_field_aug_code` | `field_aug_semantics` | `field_aug_code_state_coherent` ✓ | `field_aug_effect` — Phase-7 field-state |
| slice-set | `handle_slice_set_code` | `slice_set_semantics` | `slice_set_code_state_coherent` ✓ | `slice_effect` — array-slice semantics |
| expr-stmt | `handle_expr_code` | `expr_stmt_semantics` | `expr_code_state_coherent` ✓ | `expr_effect` — Phase-8 SCall |
| critical | `handle_critical_code` | `critical_wrapper` (eval-runs-body) | proved via its body (`emit_one_coherent`) | *none — runs its body; real concurrency = Phase 7* |

Each of the four now has a **proved** coherence lemma (✓, Z3-Valid) resting only on its atomic
`*_semantics` axiom — exactly the tier of the 10. **And the effects are now CONCRETE** (this turn):
`field`/`field-aug` = a flat field-state key update; `slice` = a region-fill (`slice_blit`, get-defined);
`expr` = identity (a discarded generic call). Effect-dependent reasoning is demonstrated
(`field_read_back`, `slice_read_in_range` proved). The only remaining primitives are value-level
(`vop`); the honest caveats are a *flat* field model (no nested-record aliasing), constant-fill `slice`,
and identity-`expr` for generic calls.

## 3b. Record-valued `val` (nested aliasing) — certified, adds NO evaluator axiom

The §3a honest caveat "a *flat* field model (no nested-record aliasing)" is now backed by a
**machine-checked value-layer certificate** for the nested-record shape — the deferred Phase-7
record-valued `val` (tier-3 plan Phase 3, T3.3.1/T3.3.2). It is delivered CONSERVATIVELY and, crucially
for this audit, **introduces no new D2 evaluator axiom**:

- **Rocq** `Phase2b_RecordVal.v` (in `_CoqProject`, built by `make`) and **Lean** `PyCSL/RecordVal.lean`
  (imported by `PyCSL.lean`, built by `lake build`) define a record/ADT-valued value `val7`/`Val7` with
  nested projection `path_get`/`pathGet` and update `path_set`/`pathSet`, and **prove** read-back
  (`o.b.c := v ⟹ o.b.c = v`), frame (`o.b.c := v` leaves `o.b.d` unchanged, `c≠d`), and
  **conservativity** against the REAL Phase-2 `lookup`/`update` (the `SAssign` WP arm is unchanged).
  This is exactly the value the Phase-1 emitter `ir_node` ADT reads: a `BinOp op left right` node is the
  record whose `ir.get("right")` read is `path_get node ["right"]`.
- **Axiom audit:** every lemma is "Closed under the global context" (Rocq) / `[propext,
  Classical.choice, Quot.sound]` (Lean) — **no axiom** beyond the standard kernel ones. `pycsl_soundness`
  / `pycslSoundnessVerified` re-prove with their axiom sets **unchanged**, so the 3-axiom trust ledger is
  intact.
- **Why no evaluator axiom:** the certificate is a *value-layer* fact about `path_get`/`path_set`; it is
  not a new emitted statement/expression shape, so it adds nothing to the `eval_whyml_*` boundary of
  §0–§2. The WhyML-side ADT node-read coupling (discriminant/`match`/projection/structural recursion) is
  carried by the Phase-0 spike `test-suite/corpus/conformance/spikes/tier3_ir_node_adt_spike.mlw`
  (positive goals Valid on Alt-Ergo+Z3; the `*_false_twin` negative controls correctly stay UNPROVEN).
- **Honest boundary (unchanged):** the *emitter* still emits **flat** `obj"."fld` keys; the record-valued
  `val` certificate exists ahead of any emitter wiring (it does not thread a `VRec` constructor into the
  core `val`/`wp` — that cascade is the Phase-1/Phase-2 emitter work). So the flat field model in §3a is
  still what the LINK-3 `pycsl-wp-spec.mlw` mirrors; this note records that the *nested-aliasing value
  model it defers to is now certified, conservatively and axiom-free*.

## 4. Expression-level audited facts (used by the composition)

| axiom | statement | justification |
|---|---|---|
| `expr_coherent` | `eval_whyml_expr (emit_expr e) st = eval_e e st` | the emitted expression string evaluates to the expression's value — the expression-level peer of the statement `*_semantics`. |
| `eval_e_int` | `eval_e e st = VInt (eval_int e st)` | the modeled fragment is int-valued (matches the VInt-centric base WP model, Phase2_State.v). Non-looping (a *separate* `eval_int`, not `vint ∘ eval_e`). |

---

## 5. Minimality & completeness for the emitted fragment

- **Minimal.** Every axiom above is *used* by a proved `*_code_state_coherent` lemma or by the
  composition (`emit_stmts_coherent`, Why3 + Rocq). Removing any one breaks a proved obligation —
  verify by deleting it and re-running `why3 prove`.
- **Complete for the emitted fragment — now ALL 15 constructs.** Every statement shape the emitter can
  produce has an audited fact here: the 10 control-flow/core arms via §1–§2 (`*_semantics`, each backed
  by a *proved* Why3 `*_code_state_coherent` lemma) and the 5 field/slice/critical/expr arms via §3a
  (provisional effect axioms, audited until a Phase 6/7/8 model proves them). `ghost-assign`/
  `ghost-array-set` reduce to `assign`/`arrayset`; `seq_assign`/`tuple_unpack` reduce to SSeq∘SAssign.
  So there is **no emitted construct outside this audited boundary** — the set is complete.
- **Irreducible.** This boundary cannot be *eliminated*: `eval_whyml_stmts` is an in-logic model of
  WhyML's own evaluation, and (Gödel/Löb) no system fully proves the soundness of its own semantics.
  "Closing" it therefore means *fully characterizing* it — which this audit does: the set is enumerated,
  each axiom cited and shown necessary, scoped to the emitted fragment, complete over all 15 constructs,
  and held separate from the machine-checked layers. That is the closure; the only further reduction
  is replacing the 5 §3a provisional effect axioms with proved per-arm lemmas as Phases 6/7/8 land.

## 6. How to re-audit

1. Confirm the axiom set is exactly this list:
   `grep -nE "^  axiom [a-z_]+_semantics|eval_empty_semantics|expr_coherent|eval_e_int" src/self-annotate/pycsl-wp-spec.mlw`
2. Confirm each is *necessary*: comment one out, `why3 prove src/self-annotate/pycsl-wp-spec.mlw -P "Z3,4.13.3,"`, expect a now-failing coherence lemma.
3. Confirm the composition's Rocq side rests only on these:
   `coqc … ; Print Assumptions emit_stmts_coherent` (in `Phase6L_ComposeIfWhile.v`) — only the per-arm
   `*_coh` axioms (= these) + the abstract interface, 0 Admitted.
4. Confirm the *soundness* side is admit-free: `Print Assumptions pycsl_soundness` → only the two
   extensionality axioms.

**Bottom line.** The audited trust for LINK-3 coherence is a **complete, minimal, cited set of ~29
evaluator axioms** (the ~24 `*_semantics`/structural/expression axioms of §1–§4, all backed by proved
`*_code_state_coherent` lemmas, plus the 5 provisional §3a effect axioms for field/slice/critical/expr)
covering **all 15 emitted constructs**, each justified against Why3's documented evaluation and the
Phase2/Phase4 model, each shown necessary, and *separate* from the machine-checked layers
(`*_code_state_coherent`, `emit_stmts_coherent`, `pycsl_soundness`, `wp_for_desugar`). This is the
irreducible D2 boundary — fully characterized here (the closure), reducible only by replacing the 5
provisional effect axioms with proofs as Phases 6/7/8 land. By design, not a gap.

---

## 7. The cross-prover bridges (items 2 & 3 of the LINK-3 remainder)

Two further correspondences sit at the trust boundary. Both are **audited, not proved** — and (like §0–§6) that is by design, with the reasons made explicit here.

### 7a. String ↔ `stmt_ir` bridge to the Rocq emitter (item 3)
The composition theorems (`PyCSL_WP_Compose.emit_stmts_coherent` in Why3, `Phase6L_ComposeIfWhile.v` in Rocq) reason about an **abstract** emitter (`emit_stmts` / the `handle_*_code` Parameters). The artifact LINK 2 validates is the **concrete Rocq** `emit_stmt_full_complete : assign_state → whyml_stmt → string` (`Phase6L_EmitBlocks.v`), checked **byte-for-byte against the Python emitter** by `bin/extraction-byte-diff.sh`.

- **Trust basis:** `bin/extraction-byte-diff.sh` — **26/26 PASS, 0 diffs** (re-verified; the standing gate).
- **Why audited, not proved:** stating the correspondence as a Why3 axiom (`∀ss. rocq_emit ss = emit_stmts ss`) makes Z3 expand the recursive `emit_stmts` and times out the composition proof; a real proof needs cross-prover *extraction equivalence* between the Why3 `handle_*_code` specs and the Rocq emitter, which is out of scope. So the `handle_*_code` Parameters are *taken to be* the LINK-2-validated emitter, and the byte-diff is the audit.
- **Strength:** empirical over the 26-case corpus, not a universal theorem — the honest status of LINK 2 throughout.

### 7b. While loop denotation adequacy (item 2)
The composition threads the loop's effect through an **abstract** `while_fix` / `eval_while_fixpoint`. Its *adequacy* — that this denotation is the real loop semantics — decomposes as:

- **The `SWhile` WP rule IS proved sound** against the SOS: `Phase5b_Soundness.v` `pycsl_soundness`, whose `Print Assumptions` are **only** `propositional_extensionality` + `functional_extensionality_dep` (no `Admitted`). So the *while semantics is not an open question* at the WP/SOS level. (The `Phase5a_WhileInv.v` `while_inv_preserved` Admitted is a separate, alternate formulation **not** in the soundness closure — verified.)
- **What stays audited:** the evaluator's `eval_while_fixpoint` denotation of the emitted while-*string* (the `while_semantics` axiom of §2) — i.e. the same evaluator-axiom trust as every other construct, nothing while-specific.
- **`wp_for_desugar` is now CLOSED** — the *for* loop: `SFor` desugars to a while; `desugar_correct`
  (SOS-level) was already proved (`Phase3b_Desugar.v`), and the **WP-level equivalence is now proved
  too** (`Phase5c_WpForDesugar.v`, `wp_for_desugar` : `wp (SFor …) ↔ wp (desugar (SFor …))`, 0 Admitted,
  `Print Assumptions` = only the two standard extensionality axioms). The hand-written SFor WP arm is a
  *proved* mirror of its desugaring, both directions.

**Net for items 2 & 3:** neither is a hidden hole. Item 3 is the (empirically-audited, 26/26) LINK-2
bridge; item 2's while semantics is *proved sound*, the for-loop WP equivalence (`wp_for_desugar`) is
now *proved*, and only the standard evaluator-axiom audit remains for the emitted while-string.
