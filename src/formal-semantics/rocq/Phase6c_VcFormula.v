(* Phase6c_VcFormula.v — vc_formula shallow embedding + denotational
   semantics + emission enumeration.

   Q3 Sub-β port (2026-05-29): extracted from Phase6m_VcgSemBridge.v
   so that `why3_certificate` (Phase6j_Why3Trust.v, downstream of
   this file in the new ordering) can be defined directly as the
   witness type, eliminating the `enrich_main_cert` axiom.

   Build-order rationale: previously the chain was
       Phase6b → Phase6j → Phase6k → Phase6L → Phase6m
   with vc_formula + vc_formula_of stranded in Phase6m. The new
   ordering is
       Phase6b → Phase6k → Phase6c → Phase6j → Phase6L → Phase6m
   so that vc_formula_of and vc_prop are both visible at the
   `why3_certificate` definition site (Phase6j). The Phase6k →
   Phase6j edge was historical-only — Phase6k did not actually
   consume any symbol from Phase6j.

   This file may NOT import Phase6j (downstream now). *)

Require Import ZArith String List Bool.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase3_SOS.
Require Import Phase4_WP.
Require Import Phase6_WhyML.
Require Import Phase6b_WPW.
Require Import Phase6k_VcgSound.
Open Scope Z_scope.

(* ===== vc_formula: shallow embedding of Why3's integer-arithmetic fragment ===== *)

Inductive vc_formula : Type :=
  | VcLe       (e1 e2 : contract_expr) : vc_formula
  | VcLt       (e1 e2 : contract_expr) : vc_formula
  | VcGe       (e1 e2 : contract_expr) : vc_formula
  | VcEq       (e1 e2 : contract_expr) : vc_formula
  | VcContract (c : contract_expr)     : vc_formula
  | VcAnd      (f1 f2 : vc_formula)   : vc_formula
  | VcImpl     (f1 f2 : vc_formula)   : vc_formula
  | VcProp     (P : Prop)             : vc_formula
  | VcTrue                            : vc_formula.

(* ===== eval_vc_formula: denotational semantics ===== *)

Fixpoint eval_vc_formula (f : vc_formula)
                         (es pre_es : exec_state) : Prop :=
  match f with
  | VcLe e1 e2     => eval_v es pre_es e1 <= eval_v es pre_es e2
  | VcLt e1 e2     => eval_v es pre_es e1 < eval_v es pre_es e2
  | VcGe e1 e2     => eval_v es pre_es e1 >= eval_v es pre_es e2
  | VcEq e1 e2     => eval_v es pre_es e1 = eval_v es pre_es e2
  | VcContract c   => eval_c es pre_es None c
  | VcAnd f1 f2    => eval_vc_formula f1 es pre_es /\ eval_vc_formula f2 es pre_es
  | VcImpl f1 f2   => eval_vc_formula f1 es pre_es -> eval_vc_formula f2 es pre_es
  | VcProp P       => P
  | VcTrue         => True
  end.

(* ===== vc_formula_of: enumerate VcFormulas for each whyml_stmt =====

   Index allocation matches Lean (VcFormula.lean).
   Z_scope is open globally — use O / S O / S (S O) for nat. *)

Definition vc_formula_of (ws : whyml_stmt) (Q : wp_conts)
                         (pre_es es : exec_state) (n : nat) : option vc_formula :=
  match ws, n with

  | WSkip, O =>
    Some (VcProp (Q.(wc_n) es))

  | WAssign x e, O =>
    Some (VcProp (Q.(wc_n) (set_reg es (update es.(reg_state) x
                                           (eval_expr es.(reg_state) e)))))

  | WAugAssign x op e, O =>
    let cur := match lookup es.(reg_state) x with
               | Some (VInt k) => k | _ => 0 end in
    let nv  := eval_binop_z op cur
                 (match eval_expr es.(reg_state) e with VInt k => k | _ => 0 end) in
    Some (VcProp (Q.(wc_n) (set_reg es (update es.(reg_state) x (VInt nv)))))

  | WArraySet arr i v, O =>
    let idx := match eval_expr es.(reg_state) i with VInt k => k | _ => 0 end in
    let nv  := match eval_expr es.(reg_state) v with VInt k => k | _ => 0 end in
    Some (VcProp (Q.(wc_n) (set_reg es (array_update es.(reg_state) arr idx nv))))

  | WSeq w1 w2, O =>
    Some (VcProp (vc_prop w1 (mkConts (fun es' => vc_prop w2 Q pre_es es')
                                        Q.(wc_r) Q.(wc_c) Q.(wc_b) Q.(wc_e))
                              pre_es es))

  | WIf cond w1 _, O =>
    Some (VcProp (eval_bool es.(reg_state) cond = true -> vc_prop w1 Q pre_es es))
  | WIf cond _ w2, S O =>
    Some (VcProp (eval_bool es.(reg_state) cond = false -> vc_prop w2 Q pre_es es))

  | WWhile invs _ _ _, O =>
    Some (VcContract (c_conj invs))
  | WWhile invs vars cond body, S O =>
    let inv := c_conj invs in
    let var := c_first vars in
    Some (VcProp (forall es',
      eval_c es' pre_es None inv ->
      eval_bool es'.(reg_state) cond = true ->
      let body_done es'' :=
        eval_c es'' pre_es None inv /\
        eval_v es'' pre_es var < eval_v es' pre_es var /\
        eval_v es'' pre_es var >= 0 in
      vc_prop body (mkConts body_done Q.(wc_r) body_done Q.(wc_n) Q.(wc_e))
                pre_es es'))
  | WWhile invs _ cond _, S (S O) =>
    let inv := c_conj invs in
    Some (VcProp (forall es',
      eval_c es' pre_es None inv ->
      eval_bool es'.(reg_state) cond = false ->
      Q.(wc_n) es'))

  | WRaise ExcReturn,     O => Some (VcProp (Q.(wc_r) es))
  | WRaise ExcBreak,      O => Some (VcProp (Q.(wc_b) es))
  | WRaise ExcContinue,   O => Some (VcProp (Q.(wc_c) es))
  | WRaise (ExcNamed nm), O => Some (VcProp (Q.(wc_e) nm es))

  | WTryCatch body exc handler, O =>
    Some (VcProp (vc_prop body
      (mkConts Q.(wc_n) Q.(wc_r) Q.(wc_c) Q.(wc_b)
               (fun exc' es' =>
                  if String.eqb exc' exc
                  then vc_prop handler Q pre_es es'
                  else Q.(wc_e) exc' es'))
      pre_es es))

  | WGhostDecl x t e, O =>
    Some (VcProp (Q.(wc_n) (set_ghost es
                               (ghost_update es.(ghost_st) x (eval_ghost_val t es e)))))

  | WGhostAssign x _ op e, O =>
    let cur := match ghost_lookup es.(ghost_st) x with Some v => v | None => GVInt 0 end in
    let nv  := apply_ghost_aug op cur es e in
    Some (VcProp (Q.(wc_n) (set_ghost es (ghost_update es.(ghost_st) x nv))))

  | WLabel L, O =>
    Some (VcProp (Q.(wc_n) (set_labels es ((L, es.(ghost_st)) :: es.(label_snaps)))))

  | WAssert cond _, O   => Some (VcContract cond)
  | WAssert _ _,   S O  => Some (VcProp (Q.(wc_n) es))

  | WAssume cond, O => Some (VcProp (eval_c es pre_es None cond -> Q.(wc_n) es))

  | _, _ => None
  end.
