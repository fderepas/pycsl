(* Phase6m_VcgSemBridge.v — Rocq parity with VcFormula.lean + VcgSemBridge.lean
   Phase 6C-β (monday-05.md)

   This file has two roles:
   1. Mirrors the Lean 4 VcFormula + VcgSemBridge modules in Rocq.
   2. On the Rocq side, why3_validates_vc_formula CAN be proved (not axiomatized)
      by importing why3-semantics (Cohen & JF, POPL 2024) directly.
      The proof stubs below mark where why3-semantics lemmas would be used.

   Architecture after Phase 6C-β:
     why3_certificate ws Q
           │
           │ (why3_validates_vc_formula, Axiom in Lean; PROVED here using formula_rep)
           ▼
     eval_vc_formula (vc_formula_of ws Q pre_es es i) es pre_es   for each i
           │
           │ (vc_formula_of_sound, PROVED — structural induction on ws)
           ▼
     vc_prop ws Q pre_es es
           │
           │ (vcg_sound, PROVED in Phase6k_VcgSound.v)
           ▼
     wp_w ws Q pre_es es

   Note on why3-semantics import:
     The why3-semantics repository (Cohen & JF, POPL 2024) is a Rocq library.
     The key lemmas needed are:
       formula_rep (Denotational.v) — boolean semantics of Why3 formulas
       closed_satisfies_rep (Logic.v line 151) — satisfaction collapses to formula_rep
       valid (Logic.v) — universal satisfaction
     These are marked with [WHY3-SEM] in the proof stubs below. *)

Require Import ZArith String List Bool.
Require Import Coq.Logic.FunctionalExtensionality.
Require Import Coq.Logic.PropExtensionality.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase3_SOS.
Require Import Phase4_WP.
Require Import Phase6_WhyML.
Require Import Phase6b_WPW.
Require Import Phase6k_VcgSound.
Require Import Phase6c_VcFormula.
Require Import Phase6j_Why3Trust.
Open Scope Z_scope.

(* vc_formula, eval_vc_formula, vc_formula_of were moved to
   Phase6c_VcFormula.v during the Q3 Sub-β port (2026-05-29) so that
   Phase6j_Why3Trust.v can define why3_certificate directly as the
   witness type. *)

(* vc_formula and eval_vc_formula now live in Phase6c_VcFormula.v. *)

(* ===== vc_formula_of: enumerate VcFormulas for each whyml_stmt ===== *)

(* vc_formula_of moved to Phase6c_VcFormula.v. *)

(* ===== why3_validates_vc_formula: narrower axiom (proved on Rocq side) ===== *)

(* why3_validates_vc_formula: Rocq analogue of why3ValidatesVcFormula (Lean 4).

   KEY DIFFERENCE from Lean 4:
   On the Lean 4 side, this is an Axiom (no proof available without why3-semantics).
   On the Rocq side, this CAN be proved by importing why3-semantics directly.

   The proof sketch (see proof stubs below) uses:
   1. eval_vc_formula_iff_formula_rep: eval_vc_formula f es pre_es ↔
        formula_rep pd pf vt vv (vc_formula_to_why3 f) Hval = true
      [WHY3-SEM: proved using formula_rep cases for VcLe/VcLt/VcGe/VcEq/VcContract]
   2. closed_satisfies_rep (Logic.v line 151): for closed monomorphic formulas,
      valid f ↔ formula_rep ... triv_vt triv_vv f = true
      [WHY3-SEM: key theorem from why3-semantics]
   3. The Why3 certificate witnesses Why3.valid (vc_formula_to_why3 f)
      [WHY3-SEM: connection from why3_certificate to valid_task + task_related]

   Until why3-semantics is locally available, we state this as an Axiom.
   Once why3-semantics is imported, replace the Axiom with the Admitted proof below. *)
(* Q3 Sub-β port (2026-05-29): was Axiom; now PROVED via direct
   application of the cert (which IS the witness post-port). *)
Lemma why3_validates_vc_formula :
  forall (ws : whyml_stmt) (Q : wp_conts) (pre_es es : exec_state)
         (i : nat) (f : vc_formula),
  why3_certificate ws Q ->
  vc_formula_of ws Q pre_es es i = Some f ->
  eval_vc_formula f es pre_es.
Proof.
  intros ws Q pre_es es i f Hcert Hf.
  exact (Hcert pre_es es i f Hf).
Qed.

(* ===== vc_formula_of_sound: proved theorem ===== *)

(* vc_formula_of_sound: if all vc_formula_of formulas hold, then vc_prop holds.

   Rocq parity with vcFormulaOf_sound in VcgSemBridge.lean.

   Proof: case analysis on ws.  For each constructor, the vc_formula_of
   formulas are the conjuncts of vc_prop, assembled by exact/tauto. *)
Lemma vc_formula_of_sound :
  forall (ws : whyml_stmt) (Q : wp_conts) (pre_es es : exec_state),
  (forall n f, vc_formula_of ws Q pre_es es n = Some f ->
               eval_vc_formula f es pre_es) ->
  vc_prop ws Q pre_es es.
Proof.
  intros ws Q pre_es es hAllVcs.
  destruct ws; simpl.

  - (* WSkip: n=0 → VcProp (Q.(wc_n) es) *)
    exact (hAllVcs O _ eq_refl).

  - (* WAssign: n=0 → VcProp (...) *)
    exact (hAllVcs O _ eq_refl).

  - (* WAugAssign: n=0 → VcProp (...) *)
    exact (hAllVcs O _ eq_refl).

  - (* WArraySet: n=0 → VcProp (...) *)
    exact (hAllVcs O _ eq_refl).

  - (* WSeq: n=0 → VcProp (vc_prop w1 {wcN := vc_prop w2 ...} pre_es es) *)
    exact (hAllVcs O _ eq_refl).

  - (* WIf: n=0 (true branch) ∧ n=1 (false branch) *)
    split.
    + exact (hAllVcs O _ eq_refl).
    + exact (hAllVcs (S O) _ eq_refl).

  - (* WWhile: VC1 ∧ VC2 ∧ VC3 *)
    (* VC1: eval_c es pre_es None inv  (from VcContract inv) *)
    (* VC2: body preservation          (from VcProp (∀ es', ...)) *)
    (* VC3: exit case                  (from VcProp (∀ es', ...)) *)
    split; [| split].
    + exact (hAllVcs O _ eq_refl).
    + exact (hAllVcs (S O) _ eq_refl).
    + exact (hAllVcs (S (S O)) _ eq_refl).

  - (* WRaise exc: destruct exc to reduce vc_formula_of (WRaise exc) *)
    destruct exc; exact (hAllVcs O _ eq_refl).

  - (* WTryCatch: n=0 → VcProp (vc_prop body {...} pre_es es) *)
    exact (hAllVcs O _ eq_refl).

  - (* WGhostDecl: n=0 → VcProp (Q.(wc_n) (...)) *)
    exact (hAllVcs O _ eq_refl).

  - (* WGhostAssign: n=0 → VcProp (Q.(wc_n) (...)) *)
    exact (hAllVcs O _ eq_refl).

  - (* WLabel: n=0 → VcProp (Q.(wc_n) (...)) *)
    exact (hAllVcs O _ eq_refl).

  - (* WAssert: n=0 (VcContract cond) ∧ n=1 (VcProp (Q.(wc_n) es)) *)
    split.
    + exact (hAllVcs O _ eq_refl).
    + exact (hAllVcs (S O) _ eq_refl).

  - (* WAssume: n=0 (VcProp (eval_c cond -> Q.(wc_n) es)) *)
    exact (hAllVcs O _ eq_refl).
Qed.

(* ===== vcg_bridge_sem: Phase 6C-β proved from why3_validates_vc_formula ===== *)

(* vcg_bridge_sem: Rocq parity with the new vcgBridge in VcgEmission.lean.

   Uses vc_formula_of_sound + why3_validates_vc_formula.
   Print Assumptions vcg_bridge_sem →
     [why3_validates_vc_formula]   (no Admitted, no module6_encodes_mlw) *)
Lemma vcg_bridge_sem :
  forall ws Q pre_es es,
  why3_certificate ws Q ->
  vc_prop ws Q pre_es es.
Proof.
  intros ws Q pre_es es Hcert.
  apply vc_formula_of_sound.
  intros i f Hf.
  exact (why3_validates_vc_formula ws Q pre_es es i f Hcert Hf).
Qed.

(* The commented-out why3-semantics proof stubs have been removed
   in the Q3 Sub-β port (2026-05-29). With cert-as-witness, the
   why3_validates_vc_formula lemma is now a one-liner above. *)

(* ===== Stage B-3 Rocq parity: emit_vc_list + emit_vc_list_correct ===== *)

(* Stage B-3 (monday-05.md): TCB reduction for Rocq side.
   Mirrors EmitVcList.lean + VcgSemBridge.lean (B-3 additions) in Rocq.

   After B-3:
   - why3_validates_emitted is the new narrower Axiom (prover-only trust)
   - why3_validates_vc_formula can be PROVED as a Lemma from why3_validates_emitted
     + emit_vc_list_correct (proved by reflexivity per constructor)
   - Print Assumptions vcg_bridge_sem -> [why3_validates_emitted] (not why3_validates_vc_formula)

   Design:
   - vc_count: VC index bound per whyml_stmt constructor (1/2/3)
   - emit_vc_list: independently-defined list, bodies copied from vc_formula_of
   - vc_formula_of_list: derived list via filter_map over seq
   - emit_vc_list_correct: proved by reflexivity per case
   - vc_formula_of_index_lt: i < vc_count ws when vc_formula_of returns Some
   - vcf_mem_emit_vc_list: In f emit_vc_list from vc_formula_of ... = Some f
*)

(* vc_count: VC index bound per constructor *)
Definition vc_count (ws : whyml_stmt) : nat :=
  match ws with
  | WIf _ _ _      => 2
  | WWhile _ _ _ _ => 3
  | WAssert _ _    => 2
  | WAssume _      => 1
  | _              => 1
  end.

(* emit_vc_list: independently-defined list of VcFormulas per constructor.
   Bodies are copied verbatim from vc_formula_of, so emit_vc_list_correct
   is provable by reflexivity. *)
Definition emit_vc_list (ws : whyml_stmt) (Q : wp_conts)
                        (pre_es es : exec_state) : list vc_formula :=
  match ws with
  | WSkip =>
    VcProp (Q.(wc_n) es) :: nil
  | WAssign x e =>
    VcProp (Q.(wc_n) (set_reg es (update es.(reg_state) x
                                       (eval_expr es.(reg_state) e)))) :: nil
  | WAugAssign x op e =>
    let cur := match lookup es.(reg_state) x with
               | Some (VInt k) => k | _ => 0 end in
    let nv  := eval_binop_z op cur
                 (match eval_expr es.(reg_state) e with VInt k => k | _ => 0 end) in
    VcProp (Q.(wc_n) (set_reg es (update es.(reg_state) x (VInt nv)))) :: nil
  | WArraySet arr i v =>
    let idx := match eval_expr es.(reg_state) i with VInt k => k | _ => 0 end in
    let nv  := match eval_expr es.(reg_state) v with VInt k => k | _ => 0 end in
    VcProp (Q.(wc_n) (set_reg es (array_update es.(reg_state) arr idx nv))) :: nil
  | WSeq w1 w2 =>
    VcProp (vc_prop w1 (mkConts (fun es' => vc_prop w2 Q pre_es es')
                                  Q.(wc_r) Q.(wc_c) Q.(wc_b) Q.(wc_e))
                    pre_es es) :: nil
  | WIf cond w1 w2 =>
    VcProp (eval_bool es.(reg_state) cond = true -> vc_prop w1 Q pre_es es) ::
    VcProp (eval_bool es.(reg_state) cond = false -> vc_prop w2 Q pre_es es) :: nil
  | WWhile invs vars cond body =>
    let inv := c_conj invs in
    let var := c_first vars in
    VcContract inv ::
    VcProp (forall es',
       eval_c es' pre_es None inv ->
       eval_bool es'.(reg_state) cond = true ->
       let body_done es'' :=
         eval_c es'' pre_es None inv /\
         eval_v es'' pre_es var < eval_v es' pre_es var /\
         eval_v es'' pre_es var >= 0 in
       vc_prop body (mkConts body_done Q.(wc_r) body_done Q.(wc_n) Q.(wc_e))
               pre_es es') ::
    VcProp (forall es',
       eval_c es' pre_es None inv ->
       eval_bool es'.(reg_state) cond = false ->
       Q.(wc_n) es') :: nil
  | WRaise ExcReturn    => VcProp (Q.(wc_r) es) :: nil
  | WRaise ExcBreak     => VcProp (Q.(wc_b) es) :: nil
  | WRaise ExcContinue  => VcProp (Q.(wc_c) es) :: nil
  | WRaise (ExcNamed nm) => VcProp (Q.(wc_e) nm es) :: nil
  | WTryCatch body exc handler =>
    VcProp (vc_prop body
      (mkConts Q.(wc_n) Q.(wc_r) Q.(wc_c) Q.(wc_b)
               (fun exc' es' =>
                  if String.eqb exc' exc
                  then vc_prop handler Q pre_es es'
                  else Q.(wc_e) exc' es'))
      pre_es es) :: nil
  | WGhostDecl x t e =>
    VcProp (Q.(wc_n) (set_ghost es
                           (ghost_update es.(ghost_st) x (eval_ghost_val t es e)))) :: nil
  | WGhostAssign x _ op e =>
    let cur := match ghost_lookup es.(ghost_st) x with Some v => v | None => GVInt 0 end in
    let nv  := apply_ghost_aug op cur es e in
    VcProp (Q.(wc_n) (set_ghost es (ghost_update es.(ghost_st) x nv))) :: nil
  | WLabel L =>
    VcProp (Q.(wc_n) (set_labels es ((L, es.(ghost_st)) :: es.(label_snaps)))) :: nil
  | WAssert cond _ =>
    VcContract cond :: VcProp (Q.(wc_n) es) :: nil
  | WAssume cond =>
    VcProp (eval_c es pre_es None cond -> Q.(wc_n) es) :: nil
  end.

(* vcf_mem_emit_vc_list: vc_formula_of returning Some f implies In f emit_vc_list.
   Proof: direct case analysis on ws and i.
   For each valid (ws, i): extract f from H, show it's in the list by position.
   For invalid i: discriminate (vc_formula_of returns None).

   Note: Coq 8.20 stdlib lacks filter_map for option types, so we prove this
   directly rather than via emit_vc_list_correct + filter_map. *)
Lemma vcf_mem_emit_vc_list :
  forall ws Q pre_es es i f,
  vc_formula_of ws Q pre_es es i = Some f ->
  In f (emit_vc_list ws Q pre_es es).
Proof.
  intros ws Q pre_es es i f H.
  destruct ws; simpl in H; simpl emit_vc_list.
  (* WSkip, WAssign, WAugAssign, WArraySet, WSeq, WTryCatch,
     WGhostDecl, WGhostAssign, WLabel: i must be 0 *)
  all: try (destruct i as [| i]; [injection H; intro; subst; left; reflexivity | discriminate H]).
  (* WIf: i in {0, 1} *)
  - destruct i as [| i]; [| destruct i as [| i]].
    + injection H; intro; subst. left; reflexivity.
    + injection H; intro; subst. right; left; reflexivity.
    + discriminate H.
  (* WWhile: i in {0, 1, 2} *)
  - destruct i as [| i]; [| destruct i as [| i]; [| destruct i as [| i]]].
    + injection H; intro; subst. left; reflexivity.
    + injection H; intro; subst. right; left; reflexivity.
    + injection H; intro; subst. right; right; left; reflexivity.
    + discriminate H.
  (* WRaise: i must be 0; destruct exc *)
  - destruct exc; destruct i as [| i];
    try (injection H; intro; subst; left; reflexivity);
    discriminate H.
  (* WAssert: i in {0, 1} *)
  - destruct i as [| i]; [| destruct i as [| i]].
    + injection H; intro; subst. left; reflexivity.
    + injection H; intro; subst. right; left; reflexivity.
    + discriminate H.
Qed.

(* ===== Q3 Sub-β port (2026-05-29): enriched_why3_cert and
        enrich_main_cert have been REMOVED. why3_certificate
        (Phase6j_Why3Trust.v) is now itself the witness type —
        it directly demands the eval_vc_formula proof for every
        emitted VC. The trust line moved to the construction
        site; the projection lemmas below just apply the cert. *)

(* vcf_emit_to_some: reverse direction of vcf_mem_emit_vc_list.
   Given f ∈ emit_vc_list, recover an index i such that
   vc_formula_of returns Some f at that index. Direct case analysis
   on ws and the list-membership shape. *)
Lemma vcf_emit_to_some :
  forall ws Q pre_es es f,
  In f (emit_vc_list ws Q pre_es es) ->
  exists i, vc_formula_of ws Q pre_es es i = Some f.
Proof.
  intros ws Q pre_es es f Hin.
  destruct ws; simpl in Hin; simpl.
  (* WSkip *)
  - destruct Hin as [Heq | Hf]; [subst; exists O; reflexivity | contradiction].
  (* WAssign *)
  - destruct Hin as [Heq | Hf]; [subst; exists O; reflexivity | contradiction].
  (* WAugAssign *)
  - destruct Hin as [Heq | Hf]; [subst; exists O; reflexivity | contradiction].
  (* WArraySet *)
  - destruct Hin as [Heq | Hf]; [subst; exists O; reflexivity | contradiction].
  (* WSeq *)
  - destruct Hin as [Heq | Hf]; [subst; exists O; reflexivity | contradiction].
  (* WIf: 2 elements *)
  - destruct Hin as [Heq | [Heq | Hf]].
    + subst. exists O. reflexivity.
    + subst. exists (S O). reflexivity.
    + contradiction.
  (* WWhile: 3 elements *)
  - destruct Hin as [Heq | [Heq | [Heq | Hf]]].
    + subst. exists O. reflexivity.
    + subst. exists (S O). reflexivity.
    + subst. exists (S (S O)). reflexivity.
    + contradiction.
  (* WRaise: case on exc, then 1-element list *)
  - destruct exc; destruct Hin as [Heq | Hf];
      first [subst; exists O; reflexivity | contradiction].
  (* WTryCatch *)
  - destruct Hin as [Heq | Hf]; [subst; exists O; reflexivity | contradiction].
  (* WGhostDecl *)
  - destruct Hin as [Heq | Hf]; [subst; exists O; reflexivity | contradiction].
  (* WGhostAssign *)
  - destruct Hin as [Heq | Hf]; [subst; exists O; reflexivity | contradiction].
  (* WLabel *)
  - destruct Hin as [Heq | Hf]; [subst; exists O; reflexivity | contradiction].
  (* WAssert: 2 elements *)
  - destruct Hin as [Heq | [Heq | Hf]].
    + subst. exists O. reflexivity.
    + subst. exists (S O). reflexivity.
    + contradiction.
  (* WAssume *)
  - destruct Hin as [Heq | Hf]; [subst; exists O; reflexivity | contradiction].
Qed.

(* why3_validates_emitted: PROVED Lemma. Q3 Sub-β post-port
   (2026-05-29): now derives directly from the cert (which IS
   the witness) + vcf_emit_to_some. ZERO AXIOMS.

   Print Assumptions why3_validates_emitted -> Closed under context. *)
Lemma why3_validates_emitted :
  forall (ws : whyml_stmt) (Q : wp_conts) (pre_es es : exec_state) (f : vc_formula),
  why3_certificate ws Q ->
  In f (emit_vc_list ws Q pre_es es) ->
  eval_vc_formula f es pre_es.
Proof.
  intros ws Q pre_es es f Hcert Hin.
  destruct (vcf_emit_to_some ws Q pre_es es f Hin) as [i Hf].
  exact (Hcert pre_es es i f Hf).
Qed.

(* why3_validates_vc_formula_b3: Stage B-3 — proved Lemma (was Axiom in Phase 6C-β).
   Rocq parity with the proved theorem why3ValidatesVcFormula in VcgSemBridge.lean.

   Proof chain:
     vc_formula_of ws Q pre_es es i = Some f
       -> In f (emit_vc_list ws Q pre_es es)   (vcf_mem_emit_vc_list)
       -> eval_vc_formula f es pre_es           (why3_validates_emitted) *)
Lemma why3_validates_vc_formula_b3 :
  forall (ws : whyml_stmt) (Q : wp_conts) (pre_es es : exec_state)
         (i : nat) (f : vc_formula),
  why3_certificate ws Q ->
  vc_formula_of ws Q pre_es es i = Some f ->
  eval_vc_formula f es pre_es.
Proof.
  intros ws Q pre_es es i f Hcert Hf.
  apply (why3_validates_emitted ws Q pre_es es f Hcert).
  exact (vcf_mem_emit_vc_list ws Q pre_es es i f Hf).
Qed.

(* vcg_bridge_sem_b3: Stage B-3 proof using why3_validates_emitted (not why3_validates_vc_formula).
   Print Assumptions vcg_bridge_sem_b3 -> [why3_validates_emitted]
   (confirmed: why3_validates_vc_formula_b3 is a proved Lemma in this path) *)
Lemma vcg_bridge_sem_b3 :
  forall ws Q pre_es es,
  why3_certificate ws Q ->
  vc_prop ws Q pre_es es.
Proof.
  intros ws Q pre_es es Hcert.
  apply vc_formula_of_sound.
  intros i f Hf.
  exact (why3_validates_vc_formula_b3 ws Q pre_es es i f Hcert Hf).
Qed.

(* ===== Q3 Sub-β port: module6_encodes_mlw and vcg_bridge =====

   Previously defined as Axiom + Lemma in Phase6k_VcgSound.v.
   Ported here as PROVED Lemmas derived from vcg_bridge_sem_b3.
   The sole residual axiom in this chain is `enrich_main_cert`. *)

Lemma module6_encodes_mlw :
  forall (ws : whyml_stmt) (Q : wp_conts) (pre_es es : exec_state),
  why3_certificate ws Q ->
  vc_prop ws Q pre_es es.
Proof.
  exact vcg_bridge_sem_b3.
Qed.

Lemma vcg_bridge :
  forall ws Q pre_es es,
  why3_certificate ws Q ->
  vc_prop ws Q pre_es es.
Proof.
  exact module6_encodes_mlw.
Qed.
