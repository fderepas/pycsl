(* Phase5c_WpForDesugar.v — closing the wp_for_desugar gap
   ============================================================================
   `wp_desugar_fwd` (Phase5b_Soundness.v) proves the FORWARD WP-coherence with
   desugaring — `wp s → wp (desugar s)` — which is what soundness uses for SFor.
   This file adds the BACKWARD direction `wp_desugar_bwd` and hence the full
   EQUIVALENCE `wp_desugar_iff : wp s ↔ wp (desugar s)`. For SFor in particular
   this closes the `wp_for_desugar` gap: the hand-written SFor WP arm is now
   PROVED equivalent (both directions) to the WP of its `SSeq∘SWhile` desugaring.

   The proof mirrors `wp_desugar_fwd` with the induction hypothesis reversed and
   `proj1`/`proj2` of the `lift_continue_wp` iff swapped.
   ========================================================================== *)

Require Import ZArith String List Bool.
Require Import Lia.
Require Import Coq.Logic.FunctionalExtensionality.
Require Import Coq.Logic.PropExtensionality.
Require Import PyCSL.Phase1_AST.
Require Import PyCSL.Phase2_State.
Require Import PyCSL.Phase3_SOS.
Require Import PyCSL.Phase3b_DesugarDef.
Require Import PyCSL.Phase3b_Desugar.
Require Import PyCSL.Phase4_WP.
Require Import PyCSL.Phase5a_WhileInv.
Require Import PyCSL.Phase7_MemModel.
Require Import PyCSL.Phase5b_Soundness.
Open Scope Z_scope.

(* wp (desugar s) → wp s : backward direction of desugaring WP-coherence. *)
Lemma wp_desugar_bwd :
  forall s Qn Qr Qc Qb Qe pre_es es,
  wp (desugar s) Qn Qr Qc Qb Qe pre_es es ->
  wp s Qn Qr Qc Qb Qe pre_es es.
Proof.
  induction s; intros Qn Qr Qc Qb Qe pre_es es Hwp; simpl in *; try exact Hwp.
  (* SSeq s1 s2 *)
  - apply IHs1 in Hwp.
    apply (wp_mono s1
             (fun es' => wp (desugar s2) Qn Qr Qc Qb Qe pre_es es')
             (fun es' => wp s2 Qn Qr Qc Qb Qe pre_es es')
             Qr Qr Qc Qc Qb Qb Qe Qe pre_es es
             (fun es' h => IHs2 Qn Qr Qc Qb Qe pre_es es' h)
             (fun es h => h) (fun es h => h) (fun es h => h) (fun exc es h => h)
             Hwp).
  (* SIf cond s1 s2 *)
  - destruct Hwp as [H1 H2]. split.
    + intro h. exact (IHs1 _ _ _ _ _ _ _ (H1 h)).
    + intro h. exact (IHs2 _ _ _ _ _ _ _ (H2 h)).
  (* SWhile inv var cond body *)
  - destruct Hwp as [hInv [hPres hPost]].
    exact (conj hInv (conj (fun es' hI hG => IHs _ Qr _ Qn Qe pre_es es' (hPres es' hI hG)) hPost)).
  (* SFor x arr inv var body: the key case (reverse of wp_desugar_fwd) *)
  - destruct Hwp as [hInv [hBody hExit]].
    refine (conj hInv (conj _ hExit)).
    intros es' hInv' hGuard.
    set (es1 := set_reg es' (update es'.(reg_state) x
                  (eval_expr es'.(reg_state) (ESubscript arr (EVar for_idx))))).
    set (bd_while := fun es'' =>
      eval_c es'' pre_es None inv /\
      eval_v es'' pre_es var < eval_v es' pre_es var /\
      eval_v es'' pre_es var >= 0).
    set (body_done := fun es'' =>
      let cur_idx := match lookup es''.(reg_state) for_idx with Some (VInt n) => n | _ => 0 end in
      let es3 := set_reg es'' (update es''.(reg_state) for_idx (VInt (cur_idx + 1))) in
      eval_c es3 pre_es None inv /\
      eval_v es3 pre_es var < eval_v es' pre_es var /\
      eval_v es3 pre_es var >= 0).
    assert (hbd_eq : forall es'', bd_while (inc_idx_fn es'') = body_done es'') by
      (intro es''; unfold bd_while, body_done, inc_idx_fn; reflexivity).
    (* hBody (from the desugar SWhile body-step) is the lift_continue form; peel it. *)
    specialize (hBody es' hInv' hGuard).
    apply (proj1 (lift_continue_wp (desugar s)
                    (fun es'' => wp (SAugAssign for_idx OpAdd (EInt 1)) bd_while Qr bd_while Qn Qe pre_es es'')
                    Qr bd_while Qn Qe pre_es es1)) in hBody.
    assert (hQn_eq : (fun es'' => wp (SAugAssign for_idx OpAdd (EInt 1)) bd_while Qr bd_while Qn Qe pre_es es'') =
                     body_done) by
      (apply functional_extensionality; intro es'';
       rewrite wp_aug_assign_for_idx; exact (hbd_eq es'')).
    assert (hQc_eq : (fun es'' => bd_while (inc_idx_fn es'')) = body_done) by
      (apply functional_extensionality; intro es''; exact (hbd_eq es'')).
    rewrite hQn_eq, hQc_eq in hBody.
    exact (IHs _ Qr _ Qn Qe pre_es es1 hBody).
  (* STryCatch s1 exc s2 *)
  - apply IHs1 in Hwp.
    apply (wp_mono s1 Qn Qn Qr Qr Qc Qc Qb Qb
             (fun exc' es' => if String.eqb exc' exc then wp (desugar s2) Qn Qr Qc Qb Qe pre_es es' else Qe exc' es')
             (fun exc' es' => if String.eqb exc' exc then wp s2 Qn Qr Qc Qb Qe pre_es es' else Qe exc' es')
             pre_es es
             (fun es h => h) (fun es h => h) (fun es h => h) (fun es h => h)).
    + intros exc' es' H.
      destruct (String.eqb_spec exc' exc) as [heq | hne].
      * exact (IHs2 Qn Qr Qc Qb Qe pre_es es' H).
      * exact H.
    + exact Hwp.
  (* SCritical mutex body *)
  - unfold critical_havoc in *; simpl in *.
    exact (IHs Qn Qr Qc Qb Qe pre_es es Hwp).
  (* SThreadEntry body *)
  - exact (IHs Qn Qr Qc Qb Qe pre_es es Hwp).
Qed.

(* Full WP-level equivalence with desugaring. *)
Theorem wp_desugar_iff :
  forall s Qn Qr Qc Qb Qe pre_es es,
  wp s Qn Qr Qc Qb Qe pre_es es <-> wp (desugar s) Qn Qr Qc Qb Qe pre_es es.
Proof.
  intros. split.
  - apply wp_desugar_fwd.
  - apply wp_desugar_bwd.
Qed.

(* wp_for_desugar: the SFor WP arm is PROVED equivalent to the WP of its
   SSeq∘SWhile desugaring — both directions. Closes the documented gap. *)
Theorem wp_for_desugar :
  forall x arr inv var body aim Qn Qr Qc Qb Qe pre_es es,
  wp (SFor x arr inv var body aim) Qn Qr Qc Qb Qe pre_es es
  <-> wp (desugar (SFor x arr inv var body aim)) Qn Qr Qc Qb Qe pre_es es.
Proof. intros. apply wp_desugar_iff. Qed.
