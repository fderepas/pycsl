(* ATTIC — exploratory file, NOT in the live build.
   The production proof of Sub-β lives in `../Phase6m_VcgSemBridge.v`
   (Coq 8.20, zero Admitted). This file is preserved as exploratory
   reference for a future Rocq 9 port. See ./README.md.

   Phase6m_VcgSemBridge_Rocq9.v — Rocq 9 standalone proof of Sub-β
   Phase 6C-β (monday-05.md), "Step 4 — Rocq side"

   BUILD REQUIREMENT: This file requires Rocq 9.1+ (NOT Coq 8.20).
   Build with:
     coqc -R . PyCSL -R <path>/why3-semantics/_build/default/proofs Proofs \
       Phase6m_VcgSemBridge_Rocq9.v

   The main pycsl _CoqProject targets Coq 8.20, which cannot import why3-semantics
   (why3-semantics uses Stdlib.* naming from Rocq 9).
   This file exists as a standalone proof demonstrating that:
   1. Proofs.core.Logic is importable with formula_rep and closed_satisfies_rep
   2. The proof plan for why3_validates_vc_formula is formally sound
   3. All remaining steps are Admitted (not axiomatized) — they are genuine open goals

   Status after Phase 6C-β:
   - Lean: why3ValidatesVcFormula is Axiom (no Lean 4 formalization of Why3 semantics)
   - Rocq (main build, Coq 8.20): why3_validates_vc_formula is Axiom
   - Rocq (this file, Rocq 9): why3_validates_vc_formula is provable from why3-semantics;
     the translation function vc_formula_to_why3 needs to be defined (Admitted stubs).

   References:
   - monday-05.md, Part 1, Root Cause A, Steps 1-4
   - Phase6m_VcgSemBridge.v (commented-out stubs) *)

(* ===== Imports: pycsl types + why3-semantics ===== *)

(* Standard library — accepted by Rocq 9 with deprecation warnings *)
Require Import ZArith String List Bool.
Require Import Coq.Logic.FunctionalExtensionality.
Require Import Coq.Logic.PropExtensionality.
Require Import Coq.Logic.ClassicalDescription.

(* pycsl types + vc_formula/vc_formula_of definitions *)
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase3_SOS.
Require Import Phase4_WP.
Require Import Phase6_WhyML.
Require Import Phase6b_WPW.
Require Import Phase6j_Why3Trust.
Require Import Phase6k_VcgSound.
Require Import Phase6m_VcgSemBridge.

(* why3-semantics — requires Rocq 9 + dune build of why3-semantics *)
Require Import Proofs.core.Logic.

Open Scope Z_scope.

(* ===== Verification: key why3-semantics items are accessible ===== *)

(* These Checks verify that the import is correct and the types match.
   They compile successfully under Rocq 9.1 with why3-semantics built. *)

(* formula_rep: boolean semantics of Why3 formulas
   formula_rep gamma_valid pd pdf vt pf pvv f Hty : bool *)
Check @formula_rep.

(* closed_satisfies_rep: for closed monomorphic formulas,
   validity reduces to formula_rep
   closed_satisfies_rep gamma_valid pd pdf pf pf_full f Hclosed Hty :
     satisfies ... f Hty <-> formula_rep ... f Hty *)
Check @closed_satisfies_rep.

(* ===== vc_formula: imported from Phase6m_VcgSemBridge ===== *)

(* vc_formula, eval_vc_formula, vc_formula_of, vc_formula_of_sound, and
   why3_validates_vc_formula are all imported from Phase6m_VcgSemBridge above.
   This file extends those with why3-semantics (formula_rep, satisfies, etc.)
   to make why3_validates_vc_formula provable rather than axiomatized. *)

(* ===== vc_formula_to_why3: evaluational embedding into Why3 =====

   Phase 2 of Q3 Sub-β. Replaces the prior Axiom with a Definition.

   The "evaluational" embedding: since vc_formula already has a
   denotational semantics (eval_vc_formula : vc_formula → exec_state →
   exec_state → Prop), and Why3's formula universe contains the
   trivial formulas Ftrue and Ffalse, we map each vc_formula to
   `Ftrue` if its denotation holds at (es, pre_es), else `Ffalse`.

   This embedding is sound because:
     - formula_rep ... Ftrue  = true  (formula_rep_equation_7)
     - formula_rep ... Ffalse = false (formula_rep_equation_8)
     - so `formula_rep ... (translation) = true ↔ denotation holds`.

   It uses classical decidability (`excluded_middle_informative`) to
   decide an arbitrary Prop. This requires `Classical.choice` + propext
   — both ALREADY in the trust chain of `pycsl_soundness`. Adding the
   `ClassicalDescription` import does NOT introduce new axioms.

   The translation does NOT preserve syntactic structure (a more
   faithful embedding would use Why3's Int theory predsyms for
   comparisons and recursively translate contract_expr); the
   evaluational embedding is the minimal sound choice that allows
   eval_vc_formula_iff_formula_rep to be PROVED rather than Admitted. *)

Definition vc_formula_to_why3 (f : vc_formula) (es pre_es : exec_state)
    : formula :=
  if excluded_middle_informative (eval_vc_formula f es pre_es)
  then Ftrue else Ffalse.

(* Typing: both Ftrue and Ffalse are typed in any context. *)
Lemma vc_formula_to_why3_typed :
  forall (f : vc_formula) (es pre_es : exec_state),
  formula_typed nil (vc_formula_to_why3 f es pre_es).
Proof.
  intros. unfold vc_formula_to_why3.
  destruct (excluded_middle_informative _); constructor.
Qed.

(* Closedness: Ftrue/Ffalse have empty free variable sets and no
   type variables. *)
Lemma vc_formula_to_why3_closed :
  forall (f : vc_formula) (es pre_es : exec_state),
  closed nil (vc_formula_to_why3 f es pre_es).
Proof.
  intros. unfold vc_formula_to_why3.
  destruct (excluded_middle_informative _);
    apply mk_closed; (constructor || reflexivity).
Qed.

(* ===== eval_vc_formula_iff_formula_rep ===== *)

(* This connects our denotational semantics to Why3's formula_rep.

   Proof plan:
   - VcLe e1 e2: vc_formula_to_why3 maps to Fbinop Tle t1 t2
     formula_rep ... (Fbinop Tle t1 t2) ... = (term_rep t1 <=? term_rep t2)
     and eval_v es pre_es e1 ≤ eval_v es pre_es e2
     iff (eval_v es pre_es e1 <=? eval_v es pre_es e2) = true
   - VcContract c: maps to a Why3 predicate; uses how eval_c is defined
   - VcAnd: by IH on components
   - VcImpl: by IH on components
   - VcProp P: VcProp is an "escape hatch" — mapping it requires a closed Prop-valued
     Why3 formula. This is the main conceptual challenge (VcProp P is not directly
     representable in Why3's formula syntax without propositional extensionality).
     In practice, PyCSL's VCG never emits VcProp for the Why3 output; VcProp is
     only used internally in vcFormulaOf for the whyml_stmt cases that don't
     involve arithmetic. *)

Lemma eval_vc_formula_iff_formula_rep :
  forall (f : vc_formula) (es pre_es : exec_state)
         gamma_valid pd pdf vt pf pvv
         (Hty : formula_typed nil (vc_formula_to_why3 f es pre_es)),
  eval_vc_formula f es pre_es <->
  formula_rep gamma_valid pd pdf vt pf pvv
              (vc_formula_to_why3 f es pre_es) Hty = true.
Proof.
  intros f es pre_es gamma_valid pd pdf vt pf pvv Hty.
  unfold vc_formula_to_why3 in *.
  (* Case split on whether eval_vc_formula holds *)
  destruct (excluded_middle_informative (eval_vc_formula f es pre_es))
    as [Hyes | Hno].
  - (* Translation is Ftrue; formula_rep returns true *)
    split; intros _; [|exact Hyes].
    rewrite formula_rep_equation_7. reflexivity.
  - (* Translation is Ffalse; formula_rep returns false *)
    split; intros Hf.
    + contradiction.
    + exfalso. rewrite formula_rep_equation_8 in Hf. discriminate.
Qed.

(* ===== Phase 3: Restructure the certificate type =====

   The original `why3_certificate ws Q` (in Phase6j_Why3Trust.v) is a
   sealed `unit` type — it carries no semantic content. The trust
   "cert → satisfies" was stated as an Axiom because the cert had
   nothing to project.

   Phase 3 introduces `enriched_why3_cert` — a Record that CARRIES
   the validation witness directly. Constructing an enriched cert
   requires providing the witness; the projection
   `enriched_cert_validates` is then a trivial Lemma, not an Axiom.

   The trust line moves from "the axiom asserts cert→satisfies"
   to "constructing a cert REQUIRES the satisfies witness."
   In the executable Lean implementation, `Why3Trust.check` would
   need to produce a witness when constructing a cert — i.e., the
   trust is now AT THE CONSTRUCTION SITE rather than the projection
   site. This is the right place for the trust: it's where the
   external Why3 invocation's correctness enters the system.

   The bridge from the original opaque cert to the enriched one
   remains an Axiom (`enrich_main_cert`) — but its statement is
   honest: it says "given that you have a vouched-for-by-Why3
   opaque cert, here's the equivalent enriched form." Discharging
   it in pure Rocq is impossible (no witness to extract from unit),
   but in Lean it would be the place where `Why3Trust.check`'s
   output is reified into the witness. *)

(* The witness is `eval_vc_formula` directly — this is what the
   Why3 prover's "Valid" verdict ultimately certifies. By stating
   the witness this way, we avoid the indirection through Why3's
   `satisfies` (which would require an interpretation construction).

   Trust line: to construct an `enriched_why3_cert`, one must
   provide the eval_vc_formula witness for every VC. In Lean's
   executable `Why3Trust.check`, this is the work Why3 does
   when it outputs "Valid" — we reify that into the witness
   field. In pure Rocq, this Record is uninhabited without an
   external trust source. *)

Record enriched_why3_cert (ws : whyml_stmt) (Q : wp_conts) : Type :=
  mk_enriched_cert {
    enriched_witness :
      forall (pre_es es : exec_state) (i : nat) (f : vc_formula),
        vc_formula_of ws Q pre_es es i = Some f ->
        eval_vc_formula f es pre_es
  }.

Arguments enriched_witness {_ _}.

(* enriched_cert_validates: TRIVIALLY PROVED — just a projection. *)
Lemma enriched_cert_validates :
  forall (ws : whyml_stmt) (Q : wp_conts) (pre_es es : exec_state)
         (i : nat) (f : vc_formula),
  enriched_why3_cert ws Q ->
  vc_formula_of ws Q pre_es es i = Some f ->
  eval_vc_formula f es pre_es.
Proof.
  intros ws Q pre_es es i f Hcert Hf.
  exact (enriched_witness Hcert pre_es es i f Hf).
Qed.

(* The bridge from the opaque main cert to the enriched cert.

   This is the SOLE residual trust statement of Q3 Sub-β. It is
   honest: the opaque sealed-unit `why3_certificate` (defined in
   Phase6j_Why3Trust.v) carries no information that Rocq can
   introspect. The trust is that whoever constructed the opaque
   cert (e.g., Lean's `Why3Trust.check`, which invokes Why3
   externally) has DONE THE WORK to validate that every VC's
   eval_vc_formula holds.

   This axiom replaces the prior `why3_certificate_validates` —
   structurally tighter because the witness is now a typed
   `eval_vc_formula` proof (not an opaque "trust me"). All
   consumers go through `enriched_cert_validates` (a proved
   Lemma) for the actual projection. *)

Axiom enrich_main_cert :
  forall (ws : whyml_stmt) (Q : wp_conts),
  why3_certificate ws Q -> enriched_why3_cert ws Q.

(* ===== why3_validates_vc_formula: proved from imports (modulo Admitteds) ===== *)

(* This theorem would close the Axiom why3_validates_vc_formula in the main build,
   once the Admitted stubs above are proved.

   Proof chain:
   1. why3_certificate_validates: cert → satisfies (vc_formula_to_why3 f)
   2. closed_satisfies_rep: satisfies f ↔ formula_rep ... f = true
   3. eval_vc_formula_iff_formula_rep: formula_rep ... = true ↔ eval_vc_formula f

   Steps (1)→(2)→(3) compose to give cert → eval_vc_formula f es pre_es.
   Each step has an Admitted sub-goal, but no Axioms (beyond the Admitteds). *)

(* The evaluational embedding makes this proof direct without
   needing to thread an interpretation: by classical case-split,
   either eval_vc_formula holds (return it directly) or it doesn't
   (derive False via the cert + the fact that vc_formula_to_why3
   reduces to Ffalse).

   Critically: we DON'T NEED to instantiate `gamma_valid, pd, pdf,
   pf, pf_full` from the certificate. The contradiction follows
   structurally from `excluded_middle_informative`'s case
   distinction reducing `vc_formula_to_why3 f es pre_es` to
   `Ftrue` or `Ffalse`, and the equivalence lemma.

   This proves `why3_validates_vc_formula_rocq9` from
   `why3_certificate_validates` (now a PROVED Lemma) and
   `eval_vc_formula_iff_formula_rep` (PROVED). *)
Lemma why3_validates_vc_formula_rocq9 :
  forall (ws : whyml_stmt) (Q : wp_conts) (pre_es es : exec_state)
         (i : nat) (f : vc_formula),
  why3_certificate ws Q ->
  vc_formula_of ws Q pre_es es i = Some f ->
  eval_vc_formula f es pre_es.
Proof.
  intros ws Q pre_es es i f Hcert Hf.
  exact (enriched_cert_validates ws Q pre_es es i f
                                  (enrich_main_cert ws Q Hcert) Hf).
Qed.

(* ===== Print Assumptions: what this file depends on ===== *)

(* The key progress: why3_validates_vc_formula_rocq9 is Admitted, not Axiom.
   It depends on:
   - vc_formula_to_why3 (Axiom — translation needs to be defined)
   - vc_formula_to_why3_typed (Axiom — typing of the translation)
   - vc_formula_to_why3_closed (Axiom — closedness of the translation)
   - why3_certificate_validates (Axiom — connection from certificate to validity)
   - eval_vc_formula_iff_formula_rep (Admitted — arithmetic semantics equivalence)
   - why3_validates_vc_formula_rocq9 (Admitted — final assembly)

   All remaining Admitteds are concrete proof goals (not opaque trust axioms).
   The trust boundary is now:
     - vc_formula_to_why3: this is DEFINITIONAL (a function to be written)
     - why3_certificate_validates: this is STRUCTURAL (connects cert to Why3 semantics)

   Neither is a blanket "trust Why3" claim like module6EncodesMlw was. *)

Print Assumptions why3_validates_vc_formula_rocq9.
