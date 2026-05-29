(* Phase6b_WPW.v — WP Semantics for the WhyML Subset
   Defines wp_conts (the exception-encoded continuation record),
   enc (packs 5 loose continuations into wp_conts),
   and wp_w (WP semantics for whyml_stmt, structurally parallel to wp).

   Key invariant: wp_w mirrors wp case-by-case.  The full correspondence
       wp s Qn Qr Qc Qb Qe pre_es es ↔ wp_w (gen s) (enc Qn Qr Qc Qb Qe) pre_es es
   is proved in Phase6h_CorrMain.v. *)

Require Import ZArith String List Bool.
Require Import Coq.Logic.FunctionalExtensionality.
Require Import Coq.Logic.PropExtensionality.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase3_SOS.   (* for eval_ghost_val, apply_ghost_aug *)
Require Import Phase4_WP.   (* for eval_c, eval_v, eval_bool, eval_expr, … *)
Require Import Phase6_WhyML.
Open Scope Z_scope.

(* ===== Exception-encoded continuation record ===== *)

Record wp_conts : Type := mkConts {
  wc_n : exec_state -> Prop;               (* normal completion *)
  wc_r : exec_state -> Prop;               (* return *)
  wc_c : exec_state -> Prop;               (* continue *)
  wc_b : exec_state -> Prop;               (* break *)
  wc_e : ident -> exec_state -> Prop       (* named exception *)
}.

(* enc: pack the five loose continuations of wp into a wp_conts record *)
Definition enc (Qn Qr Qc Qb : exec_state -> Prop)
               (Qe : ident -> exec_state -> Prop) : wp_conts :=
  mkConts Qn Qr Qc Qb Qe.

(* ===== wp_w: WP semantics for the WhyML subset ===== *)
(* Every case directly mirrors the corresponding wp case in Phase4_WP.v.
   The SWhile body continuation: break exits loop normally (wc_b := Q.(wc_n)),
   continue re-enters loop (wc_c := body_done), matching wp (SWhile ...). *)

Fixpoint wp_w (ws : whyml_stmt)
              (Q : wp_conts)
              (pre_es es : exec_state) : Prop :=
  match ws with
  | WSkip =>
      Q.(wc_n) es

  | WAssign x e =>
      Q.(wc_n) (set_reg es (update es.(reg_state) x (eval_expr es.(reg_state) e)))

  | WAugAssign x op e =>
      let cur := match lookup es.(reg_state) x with
                 | Some (VInt n) => n | _ => 0 end in
      let nv  := eval_binop_z op cur
                   (match eval_expr es.(reg_state) e with VInt n => n | _ => 0 end) in
      Q.(wc_n) (set_reg es (update es.(reg_state) x (VInt nv)))

  | WArraySet arr i v =>
      let idx := match eval_expr es.(reg_state) i with VInt n => n | _ => 0 end in
      let nv  := match eval_expr es.(reg_state) v with VInt n => n | _ => 0 end in
      Q.(wc_n) (set_reg es (array_update es.(reg_state) arr idx nv))

  | WSeq w1 w2 =>
      wp_w w1 (mkConts (fun es' => wp_w w2 Q pre_es es')
                       Q.(wc_r) Q.(wc_c) Q.(wc_b) Q.(wc_e))
           pre_es es

  | WIf cond w1 w2 =>
      (eval_bool es.(reg_state) cond = true  -> wp_w w1 Q pre_es es) /\
      (eval_bool es.(reg_state) cond = false -> wp_w w2 Q pre_es es)

  | WWhile invs vars cond body =>
      let inv := c_conj invs in
      let var := c_first vars in
      eval_c es pre_es None inv /\
      (forall es',
        eval_c es' pre_es None inv ->
        eval_bool es'.(reg_state) cond = true ->
        let body_done es'' :=
          eval_c es'' pre_es None inv /\
          eval_v es'' pre_es var < eval_v es' pre_es var /\
          eval_v es'' pre_es var >= 0 in
        (* break exits loop normally (wc_b := Q.(wc_n));
           continue re-enters loop (wc_c := body_done) *)
        wp_w body (mkConts body_done Q.(wc_r) body_done Q.(wc_n) Q.(wc_e))
             pre_es es') /\
      (forall es',
        eval_c es' pre_es None inv ->
        eval_bool es'.(reg_state) cond = false ->
        Q.(wc_n) es')

  | WRaise ExcReturn    => Q.(wc_r) es
  | WRaise ExcBreak     => Q.(wc_b) es
  | WRaise ExcContinue  => Q.(wc_c) es
  | WRaise (ExcNamed n) => Q.(wc_e) n es

  | WTryCatch body exc handler =>
      wp_w body
        (mkConts Q.(wc_n) Q.(wc_r) Q.(wc_c) Q.(wc_b)
                 (fun exc' es' =>
                    if String.eqb exc' exc
                    then wp_w handler Q pre_es es'
                    else Q.(wc_e) exc' es'))
        pre_es es

  | WGhostDecl x t e =>
      Q.(wc_n) (set_ghost es (ghost_update es.(ghost_st) x (eval_ghost_val t es e)))

  | WGhostAssign x t op e =>
      let cur := match ghost_lookup es.(ghost_st) x
                 with Some v => v | None => GVInt 0 end in
      let nv  := apply_ghost_aug op cur es e in
      Q.(wc_n) (set_ghost es (ghost_update es.(ghost_st) x nv))

  | WLabel L =>
      Q.(wc_n) (set_labels es ((L, es.(ghost_st)) :: es.(label_snaps)))

  | WAssert cond _ =>
      eval_c es pre_es None cond /\ Q.(wc_n) es
  | WAssume cond =>
      eval_c es pre_es None cond -> Q.(wc_n) es
  end.

(* ===== Monotonicity of wp_w ===== *)

Lemma wp_w_mono :
  forall ws Q Q' pre_es es,
  (forall e, Q.(wc_n) e -> Q'.(wc_n) e) ->
  (forall e, Q.(wc_r) e -> Q'.(wc_r) e) ->
  (forall e, Q.(wc_c) e -> Q'.(wc_c) e) ->
  (forall e, Q.(wc_b) e -> Q'.(wc_b) e) ->
  (forall x e, Q.(wc_e) x e -> Q'.(wc_e) x e) ->
  wp_w ws Q pre_es es ->
  wp_w ws Q' pre_es es.
Proof.
  induction ws; intros Q Q' pre_es es hn hr hc hb he Hwp; simpl in *.
  - (* WSkip *)      exact (hn _ Hwp).
  - (* WAssign *)    exact (hn _ Hwp).
  - (* WAugAssign *) exact (hn _ Hwp).
  - (* WArraySet *)  exact (hn _ Hwp).
  - (* WSeq ws1 ws2: name the inner modified continuations explicitly.
       eapply alone would unify ?Q_inner with Q (original) from exact hr/hc/hb/he. *)
    apply (IHws1
      (mkConts (fun es' => wp_w ws2 Q  pre_es es') Q.(wc_r)  Q.(wc_c)  Q.(wc_b)  Q.(wc_e))
      (mkConts (fun es' => wp_w ws2 Q' pre_es es') Q'.(wc_r) Q'.(wc_c) Q'.(wc_b) Q'.(wc_e))
      pre_es es).
    + intros es' Hes'. exact (IHws2 Q Q' pre_es es' hn hr hc hb he Hes').
    + exact hr.
    + exact hc.
    + exact hb.
    + exact he.
    + exact Hwp.
  - (* WIf: Q is unmodified; apply IHs directly. *)
    destruct Hwp as [Ht Hf]. split.
    + intro Hcond. exact (IHws1 Q Q' pre_es es hn hr hc hb he (Ht Hcond)).
    + intro Hcond. exact (IHws2 Q Q' pre_es es hn hr hc hb he (Hf Hcond)).
  - (* WWhile: name the body continuations explicitly. *)
    (* The WWhile arm uses `let inv := c_conj invs in let var := c_first vars in ...`;
       introduce these as definitional bindings for the proof. *)
    set (inv := c_conj invs) in *.
    set (var := c_first vars) in *.
    destruct Hwp as [Hinv [Hbody Hexit]].
    split; [exact Hinv | split].
    + intros es' Hinv' Hcond.
      apply (IHws
        (mkConts
           (fun es'' => eval_c es'' pre_es None inv /\
                        eval_v es'' pre_es var < eval_v es' pre_es var /\
                        eval_v es'' pre_es var >= 0)
           Q.(wc_r)
           (fun es'' => eval_c es'' pre_es None inv /\
                        eval_v es'' pre_es var < eval_v es' pre_es var /\
                        eval_v es'' pre_es var >= 0)
           Q.(wc_n)
           Q.(wc_e))
        (mkConts
           (fun es'' => eval_c es'' pre_es None inv /\
                        eval_v es'' pre_es var < eval_v es' pre_es var /\
                        eval_v es'' pre_es var >= 0)
           Q'.(wc_r)
           (fun es'' => eval_c es'' pre_es None inv /\
                        eval_v es'' pre_es var < eval_v es' pre_es var /\
                        eval_v es'' pre_es var >= 0)
           Q'.(wc_n)
           Q'.(wc_e))
        pre_es es').
      * intros es''. intro H. exact H.  (* body_done → body_done: trivial *)
      * exact hr.
      * intros es''. intro H. exact H.  (* body_done → body_done for wc_c *)
      * exact hn.
      * exact he.
      * exact (Hbody es' Hinv' Hcond).
    + intros es' Hinv' Hcond. exact (hn _ (Hexit es' Hinv' Hcond)).
  - (* WRaise *)
    destruct exc; simpl in *.
    + exact (hr _ Hwp).
    + exact (hb _ Hwp).
    + exact (hc _ Hwp).
    + exact (he _ _ Hwp).
  - (* WTryCatch: only wc_e changes; name the modified Q explicitly. *)
    apply (IHws1
      (mkConts Q.(wc_n)  Q.(wc_r)  Q.(wc_c)  Q.(wc_b)
               (fun exc' es' => if String.eqb exc' exc
                                then wp_w ws2 Q  pre_es es'
                                else Q.(wc_e)  exc' es'))
      (mkConts Q'.(wc_n) Q'.(wc_r) Q'.(wc_c) Q'.(wc_b)
               (fun exc' es' => if String.eqb exc' exc
                                then wp_w ws2 Q' pre_es es'
                                else Q'.(wc_e) exc' es'))
      pre_es es).
    + exact hn.
    + exact hr.
    + exact hc.
    + exact hb.
    + intros exc' es' Hes'. simpl in *.
      destruct (String.eqb exc' exc).
      * exact (IHws2 Q Q' pre_es es' hn hr hc hb he Hes').
      * exact (he _ _ Hes').
    + exact Hwp.
  - (* WGhostDecl *)  exact (hn _ Hwp).
  - (* WGhostAssign *) exact (hn _ Hwp).
  - (* WLabel *)      exact (hn _ Hwp).
  - (* WAssert *)
    destruct Hwp as [Hcond Hn]. split. exact Hcond. exact (hn _ Hn).
  - (* WAssume *)
    intro Hcond. exact (hn _ (Hwp Hcond)).
Qed.

(* ===== Congruence of wp_w w.r.t. extensionally equal continuations ===== *)

Lemma wp_w_congr :
  forall ws Q Q' pre_es es,
  (forall e, Q.(wc_n) e <-> Q'.(wc_n) e) ->
  (forall e, Q.(wc_r) e <-> Q'.(wc_r) e) ->
  (forall e, Q.(wc_c) e <-> Q'.(wc_c) e) ->
  (forall e, Q.(wc_b) e <-> Q'.(wc_b) e) ->
  (forall x e, Q.(wc_e) x e <-> Q'.(wc_e) x e) ->
  (wp_w ws Q pre_es es <-> wp_w ws Q' pre_es es).
Proof.
  intros ws Q Q' pre_es es hn hr hc hb he.
  split; apply wp_w_mono; intros; [
    apply hn; assumption |
    apply hr; assumption |
    apply hc; assumption |
    apply hb; assumption |
    apply he; assumption |
    apply hn; assumption |
    apply hr; assumption |
    apply hc; assumption |
    apply hb; assumption |
    apply he; assumption
  ].
Qed.
