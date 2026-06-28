(* Phase6f_Corr_Loops.v — WP Correspondence for Loop Statements
   Proves the correspondence for SWhile, SFor, SSeq, SIf, SCritical, SThreadEntry.

   These are the inductive cases that require the IH on sub-terms.
   The while case is the most involved: both wp and wp_w have the same
   3-conjunct structure, and the body IH bridges the body sub-term.

   The SWhile body continuation (from §7.6 of full6-01.md):
     wc_n = body_done   (invariant + variant decrease)
     wc_r = Qr
     wc_c = body_done   (continue re-enters loop)
     wc_b = Qn          (break exits loop normally)
     wc_e = Qe
   This matches enc body_done Qr body_done Qn Qe exactly. *)

Require Import ZArith String List Bool.
Require Import Coq.Logic.FunctionalExtensionality.
Require Import Coq.Logic.PropExtensionality.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase3b_DesugarDef.
Require Import Phase3b_Desugar.
Require Import Phase4_WP.
Require Import Phase7_MemModel.
Require Import Phase6_WhyML.
Require Import Phase6b_WPW.
Require Import Phase6c_ExprTrans.
Require Import Phase6d_StmtGen.
Require Import Phase6e_Corr_Simple.
Open Scope Z_scope.

(* ===== SSeq ===== *)

(* SSeq needs IHs for both sub-terms and wp_w_mono for the Qn continuation change. *)
Lemma wp_gen_seq :
  forall s1 s2 Qn Qr Qc Qb Qe pre_es es,
  (forall Qn' Qr' Qc' Qb' Qe' pre_es' es',
   wp s1 Qn' Qr' Qc' Qb' Qe' pre_es' es' <->
   wp_w (gen s1) (enc Qn' Qr' Qc' Qb' Qe') pre_es' es') ->
  (forall Qn' Qr' Qc' Qb' Qe' pre_es' es',
   wp s2 Qn' Qr' Qc' Qb' Qe' pre_es' es' <->
   wp_w (gen s2) (enc Qn' Qr' Qc' Qb' Qe') pre_es' es') ->
  wp (SSeq s1 s2) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (SSeq s1 s2)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof.
  intros s1 s2 Qn Qr Qc Qb Qe pre_es es IH1 IH2.
  simpl gen. simpl wp. simpl wp_w.
  (* LHS: wp s1 (fun es' => wp s2 Qn Qr Qc Qb Qe pre_es es') Qr Qc Qb Qe pre_es es
     RHS: wp_w (gen s1) (mkConts (fun es' => wp_w (gen s2) (enc Qn Qr Qc Qb Qe) pre_es es') Qr Qc Qb Qe) pre_es es *)
  rewrite (IH1 (fun es' => wp s2 Qn Qr Qc Qb Qe pre_es es') Qr Qc Qb Qe pre_es es).
  unfold enc at 1.
  apply wp_w_congr; try tauto.
  intro es'. simpl.
  exact (IH2 Qn Qr Qc Qb Qe pre_es es').
Qed.

(* ===== SIf ===== *)

Lemma wp_gen_if :
  forall cond s1 s2 Qn Qr Qc Qb Qe pre_es es,
  (forall Qn' Qr' Qc' Qb' Qe' pre_es' es',
   wp s1 Qn' Qr' Qc' Qb' Qe' pre_es' es' <->
   wp_w (gen s1) (enc Qn' Qr' Qc' Qb' Qe') pre_es' es') ->
  (forall Qn' Qr' Qc' Qb' Qe' pre_es' es',
   wp s2 Qn' Qr' Qc' Qb' Qe' pre_es' es' <->
   wp_w (gen s2) (enc Qn' Qr' Qc' Qb' Qe') pre_es' es') ->
  wp (SIf cond s1 s2) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (SIf cond s1 s2)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof.
  intros cond s1 s2 Qn Qr Qc Qb Qe pre_es es IH1 IH2.
  simpl gen. simpl wp. simpl wp_w. unfold enc. simpl.
  (* Both sides: (cond=true → IH1) /\ (cond=false → IH2).
     Full proof rewrites IH1/IH2 in each branch; admitted as future work. *)
  split; intro H; split; intro Hb.
  - exact (proj1 (IH1 Qn Qr Qc Qb Qe pre_es es) (proj1 H Hb)).
  - exact (proj1 (IH2 Qn Qr Qc Qb Qe pre_es es) (proj2 H Hb)).
  - exact (proj2 (IH1 Qn Qr Qc Qb Qe pre_es es) (proj1 H Hb)).
  - exact (proj2 (IH2 Qn Qr Qc Qb Qe pre_es es) (proj2 H Hb)).
Qed.

(* ===== SWhile ===== *)

(* The central lemma: both sides have the 3-conjunct structure.
   The body IH bridges the body sub-term with the custom body continuation. *)
Lemma wp_gen_while :
  forall inv var cond body Qn Qr Qc Qb Qe pre_es es,
  (forall Qn' Qr' Qc' Qb' Qe' pre_es' es',
   wp body Qn' Qr' Qc' Qb' Qe' pre_es' es' <->
   wp_w (gen body) (enc Qn' Qr' Qc' Qb' Qe') pre_es' es') ->
  wp (SWhile inv var cond body) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (SWhile inv var cond body)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof.
  intros inv var cond body Qn Qr Qc Qb Qe pre_es es IHbody.
  simpl gen. simpl wp. simpl wp_w.
  unfold enc. simpl.
  split; intro H.
  - destruct H as [Hinv [Hbody Hexit]].
    split; [exact Hinv | split].
    + intros es' Hinv' Hcond.
      (* The body continuation is:
           LHS: wp body body_done Qr body_done Qn Qe pre_es es'
           RHS: wp_w (gen body) {body_done, Qr, body_done, Qn, Qe} pre_es es'
                = wp_w (gen body) (enc body_done Qr body_done Qn Qe) pre_es es'  *)
      apply (IHbody (fun es'' =>
        eval_c es'' pre_es None inv /\
        eval_v es'' pre_es var < eval_v es' pre_es var /\
        eval_v es'' pre_es var >= 0)
        Qr
        (fun es'' =>
        eval_c es'' pre_es None inv /\
        eval_v es'' pre_es var < eval_v es' pre_es var /\
        eval_v es'' pre_es var >= 0)
        Qn Qe pre_es es').
      exact (Hbody es' Hinv' Hcond).
    + exact Hexit.
  - destruct H as [Hinv [Hbody Hexit]].
    split; [exact Hinv | split].
    + intros es' Hinv' Hcond.
      apply (IHbody (fun es'' =>
        eval_c es'' pre_es None inv /\
        eval_v es'' pre_es var < eval_v es' pre_es var /\
        eval_v es'' pre_es var >= 0)
        Qr
        (fun es'' =>
        eval_c es'' pre_es None inv /\
        eval_v es'' pre_es var < eval_v es' pre_es var /\
        eval_v es'' pre_es var >= 0)
        Qn Qe pre_es es').
      exact (Hbody es' Hinv' Hcond).
    + exact Hexit.
Qed.

(* ===== gen_lift_continue_wp_w: semantic meaning of gen_lift_continue ===== *)

(* gen_lift_continue inc w replaces each shallow WRaise ExcContinue with
   WSeq inc (WRaise ExcContinue).  Semantically, this replaces the wc_c
   continuation with "run inc, then fire the original wc_c".

   Hypothesis Hinc: inc's WP depends only on wc_n (the normal continuation).
   This holds for WAugAssign (the only inc used in SFor), proved below. *)

Lemma gen_lift_continue_wp_w :
  forall w inc,
  (forall Q1 Q2 pre_es1 es1,
     (forall e, Q1.(wc_n) e <-> Q2.(wc_n) e) ->
     (wp_w inc Q1 pre_es1 es1 <-> wp_w inc Q2 pre_es1 es1)) ->
  forall Q pre_es es,
  wp_w (gen_lift_continue inc w) Q pre_es es
  <->
  wp_w w (mkConts Q.(wc_n)
                  Q.(wc_r)
                  (fun es' => wp_w inc
                                (mkConts Q.(wc_c) Q.(wc_r) Q.(wc_c) Q.(wc_b) Q.(wc_e))
                                pre_es es')
                  Q.(wc_b)
                  Q.(wc_e))
         pre_es es.
Proof.
  intros w inc Hinc.
  induction w; intros Q pre_es es.
  (* WSkip *)       - simpl. tauto.
  (* WAssign *)     - simpl. tauto.
  (* WAugAssign *)  - simpl. tauto.
  (* WArraySet *)   - simpl. tauto.
  (* WSeq w1 w2 *)
  - simpl gen_lift_continue. simpl wp_w.
    rewrite (IHw1 (mkConts (fun es' => wp_w (gen_lift_continue inc w2) Q pre_es es')
                           Q.(wc_r) Q.(wc_c) Q.(wc_b) Q.(wc_e)) pre_es es).
    apply wp_w_congr; try tauto.
    intro es'. simpl. exact (IHw2 Q pre_es es').
  (* WIf cond w1 w2 *)
  - simpl gen_lift_continue. simpl wp_w.
    split; intros [H1 H2]; split.
    + intro Hb. exact (proj1 (IHw1 Q pre_es es) (H1 Hb)).
    + intro Hb. exact (proj1 (IHw2 Q pre_es es) (H2 Hb)).
    + intro Hb. exact (proj2 (IHw1 Q pre_es es) (H1 Hb)).
    + intro Hb. exact (proj2 (IHw2 Q pre_es es) (H2 Hb)).
  (* WWhile: gen_lift_continue is identity; wc_c not used by WWhile *)
  - simpl gen_lift_continue. simpl wp_w. tauto.
  (* WRaise exc *)
  - destruct exc.
    + simpl. tauto.   (* ExcReturn *)
    + simpl. tauto.   (* ExcBreak *)
    + (* ExcContinue: becomes WSeq inc (WRaise ExcContinue) *)
      simpl gen_lift_continue. simpl wp_w.
      apply Hinc. intro e_val. split; intro H; exact H.
    + simpl. tauto.   (* ExcNamed n *)
  (* WTryCatch body exc handler *)
  - simpl gen_lift_continue. simpl wp_w.
    rewrite (IHw1 (mkConts Q.(wc_n) Q.(wc_r) Q.(wc_c) Q.(wc_b)
                           (fun exc' es' =>
                              if String.eqb exc' exc then
                                wp_w (gen_lift_continue inc w2) Q pre_es es'
                              else Q.(wc_e) exc' es'))
                  pre_es es).
    apply wp_w_congr; try tauto.
    + (* wc_c: Hinc applies since only wc_n of the inner Q matters *)
      intro es'. simpl. apply Hinc. intro e_val. simpl. tauto.
    + (* wc_e: dispatch on whether exc' matches; use rewrite Heq to reduce if *)
      intros exc' es'. simpl.
      destruct (String.eqb exc' exc) eqn:Heq.
      * simpl. exact (IHw2 Q pre_es es').
      * simpl. tauto.
  (* WGhostDecl *)   - simpl. tauto.
  (* WGhostAssign *) - simpl. tauto.
  (* WLabel *)       - simpl. tauto.
  (* WAssert *)      - simpl. tauto.
  (* WAssume *)      - simpl. tauto.
Qed.

(* ===== SFor ===== *)

(* The SFor case reduces to SWhile via the inlined desugaring in gen.
   Key steps:
   1. Both sides expand to the same 3-conjunct while structure.
   2. For the body conjunct, gen_lift_continue_wp_w converts
      gen_lift_continue inc (gen body) to gen body with modified wc_c.
   3. wp_w_congr equates the modified wc_c with body_done (definitionally
      after simpl: wp_w (WAugAssign for_idx OpAdd 1) Q pre_es es'' reduces
      to Q.wc_n applied to the state with for_idx incremented, matching
      body_done exactly).
   4. IHbody closes the gap between wp body and wp_w (gen body). *)
Lemma wp_gen_for :
  forall x arr inv var body aim Qn Qr Qc Qb Qe pre_es es,
  (forall Qn' Qr' Qc' Qb' Qe' pre_es' es',
   wp body Qn' Qr' Qc' Qb' Qe' pre_es' es' <->
   wp_w (gen body) (enc Qn' Qr' Qc' Qb' Qe') pre_es' es') ->
  wp (SFor x arr inv var body aim) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (SFor x arr inv var body aim)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof.
  intros x arr inv var body aim Qn Qr Qc Qb Qe pre_es es IHbody.
  simpl gen. simpl wp. simpl wp_w.
  (* Hinc: WAugAssign for_idx fires only wc_n regardless of other continuations *)
  assert (Hinc : forall Q1 Q2 pe e1,
    (forall ev, Q1.(wc_n) ev <-> Q2.(wc_n) ev) ->
    wp_w (WAugAssign for_idx OpAdd (EInt 1)) Q1 pe e1 <->
    wp_w (WAugAssign for_idx OpAdd (EInt 1)) Q2 pe e1).
  { intros Q1 Q2 pe e1 H. simpl wp_w. apply H. }
  split; intros [Hinv [Hbody Hexit]].
  (* → direction: wp (SFor ...) → wp_w (gen (SFor ...)) *)
  - split; [exact Hinv | split; [| exact Hexit]].
    intros es' Hinv' Hguard.
    specialize (Hbody es' Hinv' Hguard).
    set (inc := WAugAssign for_idx OpAdd (EInt 1)).
    set (es1 := set_reg es'
                  (update es'.(reg_state) x
                     (eval_expr es'.(reg_state) (ESubscript arr (EVar for_idx))))).
    (* bdw: invariant/variant predicate checked AFTER the increment step *)
    set (bdw := fun es'' : exec_state =>
      eval_c es'' pre_es None inv /\
      eval_v es'' pre_es var < eval_v es' pre_es var /\
      eval_v es'' pre_es var >= 0).
    (* bd: predicate on the body-exit state, BEFORE the inc step;
       bd es'' = bdw (after applying inc to es'') = body_done from wp (SFor ...) *)
    set (bd := fun es'' : exec_state =>
      let cur_idx :=
        match lookup es''.(reg_state) for_idx with Some (VInt n) => n | _ => 0 end in
      bdw (set_reg es'' (update es''.(reg_state) for_idx (VInt (cur_idx + 1))))).
    (* After simpl, Hbody has the inline form of bd; change uses definitional equality *)
    change (wp body bd Qr bd Qn Qe pre_es es1) in Hbody.
    (* Apply IHbody (→): wp body bd ... → wp_w (gen body) (enc bd ...) ... *)
    apply (proj1 (IHbody bd Qr bd Qn Qe pre_es es1)) in Hbody.
    (* Goal after simpl wp_w: wp_w (gen_lift_continue inc (gen body)) (mkConts bd Qr bdw Qn Qe) pre_es es1
       Use change since set did not fold the inline wc_n to bd *)
    change (wp_w (gen_lift_continue inc (gen body)) (mkConts bd Qr bdw Qn Qe) pre_es es1).
    (* Apply gen_lift_continue_wp_w (←): goal reduces to wp_w (gen body) Q_mod pre_es es1
       where Q_mod.wc_c = fun es'' => wp_w inc (mkConts bdw ...) pre_es es'' ≡ bd (definitionally).
       Therefore Q_mod ≡ enc bd Qr bd Qn Qe, so exact Hbody closes the goal. *)
    apply (proj2 (gen_lift_continue_wp_w (gen body) inc Hinc (mkConts bd Qr bdw Qn Qe) pre_es es1)).
    exact Hbody.
  (* ← direction: wp_w (gen (SFor ...)) → wp (SFor ...) *)
  - split; [exact Hinv | split; [| exact Hexit]].
    intros es' Hinv' Hguard.
    specialize (Hbody es' Hinv' Hguard).
    set (inc := WAugAssign for_idx OpAdd (EInt 1)).
    set (es1 := set_reg es'
                  (update es'.(reg_state) x
                     (eval_expr es'.(reg_state) (ESubscript arr (EVar for_idx))))).
    set (bdw := fun es'' : exec_state =>
      eval_c es'' pre_es None inv /\
      eval_v es'' pre_es var < eval_v es' pre_es var /\
      eval_v es'' pre_es var >= 0).
    set (bd := fun es'' : exec_state =>
      let cur_idx :=
        match lookup es''.(reg_state) for_idx with Some (VInt n) => n | _ => 0 end in
      bdw (set_reg es'' (update es''.(reg_state) for_idx (VInt (cur_idx + 1))))).
    (* Hbody has the fully expanded WhyML form; change to the abbreviated form *)
    change (wp_w (gen_lift_continue inc (gen body)) (mkConts bd Qr bdw Qn Qe) pre_es es1) in Hbody.
    (* Apply gen_lift_continue_wp_w (→): Hbody becomes wp_w (gen body) Q_mod pre_es es1
       where Q_mod.wc_c ≡ bd definitionally *)
    apply (proj1 (gen_lift_continue_wp_w (gen body) inc Hinc (mkConts bd Qr bdw Qn Qe) pre_es es1)) in Hbody.
    (* Goal: wp body bd Qr bd Qn Qe pre_es es1 (after change) *)
    change (wp body bd Qr bd Qn Qe pre_es es1).
    (* Apply IHbody (←): wp_w (gen body) (enc bd ...) → wp body bd ...
       exact Hbody works because enc bd Qr bd Qn Qe ≡ Q_mod definitionally *)
    exact (proj2 (IHbody bd Qr bd Qn Qe pre_es es1) Hbody).
Qed.

(* ===== SCritical / SThreadEntry (transparent) ===== *)

Lemma wp_gen_critical :
  forall mutex body Qn Qr Qc Qb Qe pre_es es,
  (forall Qn' Qr' Qc' Qb' Qe' pre_es' es',
   wp body Qn' Qr' Qc' Qb' Qe' pre_es' es' <->
   wp_w (gen body) (enc Qn' Qr' Qc' Qb' Qe') pre_es' es') ->
  wp (SCritical mutex body) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (SCritical mutex body)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof.
  intros mutex body Qn Qr Qc Qb Qe pre_es es IHbody.
  simpl gen. simpl wp. unfold critical_havoc in *.
  exact (IHbody Qn Qr Qc Qb Qe pre_es es).
Qed.

Lemma wp_gen_thread_entry :
  forall body Qn Qr Qc Qb Qe pre_es es,
  (forall Qn' Qr' Qc' Qb' Qe' pre_es' es',
   wp body Qn' Qr' Qc' Qb' Qe' pre_es' es' <->
   wp_w (gen body) (enc Qn' Qr' Qc' Qb' Qe') pre_es' es') ->
  wp (SThreadEntry body) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (SThreadEntry body)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof.
  intros body Qn Qr Qc Qb Qe pre_es es IHbody.
  simpl gen. simpl wp.
  exact (IHbody Qn Qr Qc Qb Qe pre_es es).
Qed.
